#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module containing utility functions for the scraper.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

# Logging configuration


def setup_logging():
    """Configure and return a logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def read_yaml_file(file_path: str) -> Optional[Dict]:
    """
    Read and return the content of a YAML file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        The content of the YAML file or None in case of error.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            yaml_content = yaml.safe_load(file)
            return yaml_content
    except (yaml.YAMLError, FileNotFoundError) as e:
        logger.error(f"Error reading YAML file: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """
    Clean a string to make it usable as a filename.

    Args:
        filename: The filename to clean.

    Returns:
        The cleaned filename.
    """
    return "".join(c if c.isalnum() or c in [' ', '_', '-'] else '_' for c in filename)


def ensure_directory(directory: Path) -> Path:
    """
    Ensure a directory exists, create it if necessary.

    Args:
        directory: The path of the directory to check/create.

    Returns:
        The path of the directory.
    """
    directory.mkdir(parents=True, exist_ok=True)
    return directory
