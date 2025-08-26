#!/usr/bin/env python3
"""
Test script for Obsidian backup tool.
This creates a test vault structure and tests the backup functionality.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def create_test_vault(vault_path):
    """Create a test Obsidian vault structure"""
    os.makedirs(vault_path, exist_ok=True)

    # Create .obsidian directory with config files
    obsidian_dir = os.path.join(vault_path, ".obsidian")
    os.makedirs(obsidian_dir, exist_ok=True)

    # Create sample config files
    config_files = {
        "app.json": '{"version": "1.0.0"}',
        "core-plugins.json": '["file-explorer", "search"]',
        "plugins.json": "{}",
    }

    for filename, content in config_files.items():
        with open(os.path.join(obsidian_dir, filename), "w") as f:
            f.write(content)

    # Create sample markdown files
    sample_notes = {
        "Welcome.md": "# Welcome to Obsidian\nThis is a test note.",
        "Daily Notes/2025-01-01.md": "# January 1, 2025\nToday's thoughts...",
        "Projects/Project A.md": "# Project A\n- [ ] Task 1\n- [ ] Task 2",
    }

    for filepath, content in sample_notes.items():
        full_path = os.path.join(vault_path, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    print(f"Created test vault at: {vault_path}")


def test_backup():
    """Test the backup functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = os.path.join(temp_dir, "test_vault")
        create_test_vault(vault_path)

        # Create backup directory
        backup_dir = os.path.join(temp_dir, "backups")

        # Create test config
        config_content = f"""[backup]
vault_path = {vault_path}
backup_dir = {backup_dir}
retain_count = 3
"""

        config_path = os.path.join(temp_dir, "test_config.ini")
        with open(config_path, "w") as f:
            f.write(config_content)

        print("Running backup test...")
        print(f"Vault: {vault_path}")
        print(f"Backup: {backup_dir}")

        # Run backup tool with custom config
        result = subprocess.run(
            [sys.executable, "main.py", "--config", config_path],
            cwd=os.getcwd(),
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )

        if result.returncode == 0:
            print("✅ Backup test completed successfully!")

            # Check if backup files were created
            backup_files = list(Path(backup_dir).glob("obsidian_backup_*.zip"))
            if backup_files:
                print(f"✅ Created {len(backup_files)} backup file(s)")
                for file in backup_files:
                    print(f"   - {file.name} ({file.stat().st_size} bytes)")
            else:
                print("❌ No backup files found")
                return False

        else:
            print("❌ Backup test failed")
            return False

        # Test multiple backups to check version management
        print("\nTesting version management...")
        for i in range(3):
            result = subprocess.run(
                [sys.executable, "main.py", "--config", config_path],
                cwd=os.getcwd(),
                env={**os.environ, "PYTHONPATH": os.getcwd()},
            )

            if result.returncode != 0:
                print(f"❌ Additional backup #{i + 1} failed")
                return False

        # Check that only 3 backups are retained
        backup_files = sorted(
            Path(backup_dir).glob("obsidian_backup_*.zip"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        print(f"Found backup files: {[f.name for f in backup_files]}")
        print(f"File sizes: {[f.stat().st_size for f in backup_files]}")

        if len(backup_files) == 3:
            print("✅ Version management working correctly - retained 3 backups")
        else:
            print(f"❌ Expected 3 backups, found {len(backup_files)}")
            return False

        return True


if __name__ == "__main__":
    import sys

    success = test_backup()
    sys.exit(0 if success else 1)
