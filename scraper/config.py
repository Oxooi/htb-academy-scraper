#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration management module for the scraper.
"""

from typing import Dict, Optional
from pathlib import Path
from .utils import read_yaml_file, logger

DEFAULT_CONFIG_PATH = Path("./config/config.yaml")


class Config:
    """Configuration management class."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration.

        Args:
            config_path: Path to the configuration file.
                If None, uses the default path.
        """
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config_data = self._load_config()

    def _load_config(self) -> Dict:
        """
        Load configuration data from the file.

        Returns:
            The configuration data or an empty dictionary in case of error.
        """
        config_data = read_yaml_file(str(self.config_path))
        if not config_data:
            logger.error(
                f"Unable to load configuration from {self.config_path}")
            return {}
        return config_data

    @property
    def url(self) -> str:
        """Returns the base URL."""
        url = self.config_data.get('url', '')
        if not url:
            logger.warning("URL missing in configuration")
        return url

    @property
    def file(self) -> str:
        """Returns the filename for storing links."""
        return self.config_data.get('file', 'links.txt')

    @property
    def cookies(self) -> Dict:
        """Returns cookies for HTTP requests."""
        return self.config_data.get('cookies', {})

    def is_valid(self) -> bool:
        """
        Checks if the configuration is valid.

        Returns:
            True if the configuration is valid, False otherwise.
        """
        return bool(self.url)
