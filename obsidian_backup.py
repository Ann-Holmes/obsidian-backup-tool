#!/usr/bin/env python3
"""
Obsidian Vault Backup Tool
A simple tool to backup Obsidian vaults to local directory with version management.
"""

import os
import sys
import zipfile
import configparser
import logging
from pathlib import Path
from datetime import datetime
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("obsidian_backup.log"), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class ObsidianBackup:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.environ.get("BACKUP_CONFIG", "backup_config.ini")
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from INI file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file '{self.config_path}' not found")

        self.config.read(self.config_path)

        # Validate required settings
        required_sections = ["backup"]
        required_keys = ["vault_path", "backup_dir", "retain_count"]

        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing section '{section}' in configuration")

            for key in required_keys:
                if key not in self.config[section]:
                    raise ValueError(f"Missing key '{key}' in section '{section}'")

    def get_backup_settings(self) -> dict:
        """Get backup settings from configuration"""
        return {
            "vault_path": self.config["backup"]["vault_path"],
            "backup_dir": self.config["backup"]["backup_dir"],
            "retain_count": int(self.config["backup"]["retain_count"]),
        }

    def create_backup_filename(self) -> str:
        """Generate backup filename with timestamp including milliseconds"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"obsidian_backup_{timestamp}.zip"

    def zip_directory(self, source_dir: str, output_zip: str) -> bool:
        """Create zip archive of directory"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                logger.error(f"Source directory does not exist: {source_dir}")
                return False

            with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Use relative path for zip archive
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
                        logger.debug(f"Added to backup: {arcname}")

            logger.info(f"Backup created successfully: {output_zip}")
            return True

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

    def get_existing_backups(self, backup_dir: str) -> List[str]:
        """Get list of existing backup files sorted by modification time"""
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            return []

        backup_files = []
        for file in backup_path.glob("obsidian_backup_*.zip"):
            backup_files.append(str(file))

        # Sort by modification time (newest first)
        backup_files.sort(key=os.path.getmtime, reverse=True)
        return backup_files

    def cleanup_old_backups(self, backup_dir: str, retain_count: int) -> None:
        """Remove old backups beyond retention count"""
        backup_files = self.get_existing_backups(backup_dir)

        if len(backup_files) > retain_count:
            files_to_delete = backup_files[retain_count:]
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old backup: {file_path}")
                except Exception as e:
                    logger.error(f"Error deleting backup {file_path}: {e}")

    def run_backup(self) -> bool:
        """Execute the backup process"""
        try:
            settings = self.get_backup_settings()
            vault_path = settings["vault_path"]
            backup_dir = settings["backup_dir"]
            retain_count = settings["retain_count"]

            logger.info(f"Starting backup of: {vault_path}")
            logger.info(f"Backup destination: {backup_dir}")
            logger.info(f"Retaining {retain_count} backups")

            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)

            # Generate backup filename
            backup_filename = self.create_backup_filename()
            backup_path = os.path.join(backup_dir, backup_filename)

            # Create backup
            if not self.zip_directory(vault_path, backup_path):
                return False

            # Cleanup old backups
            self.cleanup_old_backups(backup_dir, retain_count)

            logger.info("Backup completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False


def main():
    """Main function"""
    try:
        backup_tool = ObsidianBackup()
        success = backup_tool.run_backup()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
