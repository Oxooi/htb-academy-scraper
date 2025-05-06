#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the scraper.
"""

import os
import sys
from pathlib import Path

from .config import Config
from .scraper import WebScraper, ContentScraper
from .utils import logger
import time
import random


def run():
    """Main function to run the scraper."""
    try:
        # Load configuration
        config = Config()
        if not config.is_valid():
            logger.error("Invalid configuration. Check your config.yaml file.")
            sys.exit(1)

        # Initialize main scraper
        main_scraper = WebScraper(
            config.url, config.file, config.cookies, config.url)

        # Create output directory and change to it
        output_dir = main_scraper.create_output_directory()
        original_dir = Path.cwd()
        os.chdir(output_dir)

        # Extract and save links
        links = main_scraper.extract_links()
        if not links:
            logger.warning("No links found to scrape.")
            os.chdir(original_dir)
            return

        main_scraper.save_links_to_file(links)

        # Scrape content for each link
        total_links = len(links)
        logger.info(f"Starting to scrape {total_links} pages...")

        for i, link in enumerate(links, 1):
            logger.info(f"[{i}/{total_links}] Scraping {link}")

            # Create a scraper for the specific content
            content_scraper = ContentScraper(
                link, config.file, config.cookies, config.url, i)

            # Extract and save content
            title, content = content_scraper.extract_content()
            if content:
                content_scraper.save_content(title, content)
            # Add seconds delay to avoid ban
            time.sleep(1 + (2 * random.random()))  # Add a random delay between 1 and 3 seconds

        # Cleanup: remove temporary links file
        temp_file = Path(config.file)
        if temp_file.exists():
            temp_file.unlink()

        logger.info(
            f"Scraping completed! {total_links} pages have been successfully scraped.")
        os.chdir(original_dir)

    except KeyboardInterrupt:
        logger.info("Scraper stopped by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    run()
