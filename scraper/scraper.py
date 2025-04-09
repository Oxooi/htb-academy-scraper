#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main scraping module for extracting content from web pages.
"""

import requests
from bs4 import BeautifulSoup as bs
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

from .utils import logger, sanitize_filename, ensure_directory


class WebScraper:
    """Class for scraping links and their content from a given URL."""

    def __init__(self, url: str, file: str, cookies: Dict, base_url: str):
        """
        Initialize the scraper.

        Args:
            url: The URL to scrape.
            file: The file to store links.
            cookies: The cookies to use for requests.
            base_url: The base URL for relative links.
        """
        self.url = url
        self.file = file
        self.cookies = cookies
        self.base_url = base_url

    def get_soup(self) -> Optional[bs]:
        """
        Make a request to the URL and parse the HTML content.

        Returns:
            The BeautifulSoup object containing the parsed HTML or None in case of error.
        """
        try:
            logger.debug(f"Request to {self.url}")
            response = requests.get(self.url, cookies=self.cookies, timeout=10)
            response.raise_for_status()
            return bs(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {self.url}: {e}")
            return None

    def get_title(self) -> str:
        """
        Get the title of the web page.

        Returns:
            The title of the web page or a default title.
        """
        soup = self.get_soup()
        if not soup or not soup.title:
            logger.warning(f"Unable to retrieve title for {self.url}")
            return "Untitled_Content"
        return soup.title.get_text().strip()

    def create_output_directory(self) -> Path:
        """
        Create the output directory for results.

        Returns:
            The path to the created directory.
        """
        title = self.get_title()
        safe_title = sanitize_filename(title)

        # Create 'results' folder and the subfolder with the title
        results_path = Path('results')
        title_path = results_path / safe_title

        return ensure_directory(title_path)

    def extract_links(self) -> List[str]:
        """
        Extract links from the web page.

        Returns:
            The list of found links.
        """
        soup = self.get_soup()
        if not soup:
            return []

        try:
            toc = soup.find('div', {'id': 'TOC'})
            if not toc:
                logger.warning(f"No table of contents found for {self.url}")
                return []

            links = []
            for link_tag in toc.find_all('a'):
                href = link_tag.get('href')
                if href:
                    # Convert relative links to absolute URLs
                    full_url = urljoin(self.base_url, href)
                    links.append(full_url)

            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []

    def save_links_to_file(self, links: List[str]) -> bool:
        """
        Save links to a file.

        Args:
            links: The list of links to save.

        Returns:
            True if the save succeeded, False otherwise.
        """
        try:
            with open(self.file, 'w', encoding='utf-8') as f:
                for link in links:
                    f.write(f"{link}\n")
            return True
        except IOError as e:
            logger.error(f"Error saving links: {e}")
            return False


class ContentScraper(WebScraper):
    """Class for scraping content from a specific page."""

    def __init__(self, url: str, file: str, cookies: Dict, base_url: str, index: int = 1):
        """
        Initialize the content scraper.

        Args:
            url: The URL to scrape.
            file: The file to store links.
            cookies: The cookies to use for requests.
            base_url: The base URL for relative links.
            index: The index for numbering files.
        """
        super().__init__(url, file, cookies, base_url)
        self.index = index

    def extract_content(self) -> Tuple[str, str]:
        """
        Extract the main content of the page.

        Returns:
            A tuple containing the title and HTML content.
        """
        soup = self.get_soup()
        if not soup:
            return "Error", ""

        try:
            content_div = soup.find('div', {'class': 'training-module'})
            if not content_div:
                logger.warning(f"No content found for {self.url}")
                return "No content", ""

            title_elem = content_div.find('h1')
            title = title_elem.text.strip() if title_elem else "Untitled"
            content = content_div.decode_contents()

            return title, content
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return "Error", ""

    def save_content(self, title: str, content: str) -> Path:
        """
        Save content to a file.

        Args:
            title: The title of the content.
            content: The HTML content to save.

        Returns:
            The path to the created file.
        """
        if not content:
            logger.warning(f"No content to save for {self.url}")
            return Path()

        try:
            # Create folder name with index and title
            folder_name = f"{self.index:03d}_{sanitize_filename(title)}"
            output_dir = Path.cwd() / folder_name
            ensure_directory(output_dir)

            # Create output file
            output_file = output_dir / f"{folder_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Content saved: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving content: {e}")
            return Path()
