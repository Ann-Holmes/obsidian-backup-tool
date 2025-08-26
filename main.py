#!/usr/bin/env python3
"""
Obsidian Vault Backup Tool - Command Line Interface
Entry point for the backup tool with command line argument support.
"""

import argparse
import logging
import os
import sys

from obsidian_backup import ObsidianBackup


def setup_logging(verbose: bool = False) -> None:
    """Configure logging based on verbosity level"""
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("obsidian_backup.log"),
            logging.StreamHandler(sys.stdout)
        ],
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Backup Obsidian vaults with version management"
    )

    parser.add_argument(
        "-c", "--config",
        default=os.environ.get("BACKUP_CONFIG", "backup_config.ini"),
        help="Path to configuration file (default: backup_config.ini "
             "or BACKUP_CONFIG env var)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output with debug logging"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate backup without actually creating files"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the backup tool"""
    args = parse_arguments()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("Starting Obsidian Backup Tool")

    try:
        backup_tool = ObsidianBackup(args.config)

        if args.dry_run:
            logger.info("Dry run mode - simulating backup")
            settings = backup_tool.get_backup_settings()
            logger.info(f"Vault path: {settings['vault_path']}")
            logger.info(f"Backup directory: {settings['backup_dir']}")
            logger.info(f"Retain count: {settings['retain_count']}")
            logger.info("Dry run completed successfully")
            return 0

        success = backup_tool.run_backup()
        if success:
            logger.info("Backup completed successfully!")
            return 0
        else:
            logger.error("Backup failed")
            return 1

    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Configuration validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
