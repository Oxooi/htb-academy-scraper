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
            return bs(response.content, "html.parser")
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
        results_path = Path("results")
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
            toc = soup.find("div", {"id": "TOC"})
            if not toc:
                logger.warning(f"No table of contents found for {self.url}")
                return []

            links = []
            for link_tag in toc.find_all("a"):
                href = link_tag.get("href")
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
            with open(self.file, "w", encoding="utf-8") as f:
                for link in links:
                    f.write(f"{link}\n")
            return True
        except IOError as e:
            logger.error(f"Error saving links: {e}")
            return False


class ContentScraper(WebScraper):
    """Class for scraping content from a specific page."""

    def __init__(
        self, url: str, file: str, cookies: Dict, base_url: str, index: int = 1
    ):
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
            content_div = soup.find("div", {"class": "training-module"})
            if not content_div:
                logger.warning(f"No content found for {self.url}")
                return "No content", ""

            title_elem = content_div.find("h1")
            title = title_elem.text.strip() if title_elem else "Untitled"
            content = content_div.decode_contents()

            return title, content
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return "Error", ""

    def convert_content(self, title: str, content: str) -> str:
        """
        Convert the HTML content into Markdown format.

        Args:
            title: The title of the content.
            content: The HTML content to convert.

        Returns:
            The content formatted in Markdown.
        """
        if not content:
            logger.warning(f"No content to convert for {self.url}")
            return ""

        try:
            # Create BeautifulSoup object from HTML content
            soup = bs(content, "html.parser")

            # Initialize markdown content with title
            markdown = f"# {title}\n\n"

            # Process all content elements
            for element in soup.find_all(
                [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "p",
                    "img",
                    "pre",
                    "table",
                    "ul",
                    "ol",
                    "div",
                ],
                recursive=False,
            ):
                markdown += self._process_element(element)

            # Clean up markdown by removing excessive newlines
            markdown = self._clean_markdown(markdown)

            return markdown

        except Exception as e:
            logger.error(f"Error converting content to markdown: {e}")
            return content  # Return original content on error

    def _process_element(self, element):
        """Process a single HTML element and return its markdown representation."""
        markdown = ""

        # Headings
        if element.name.startswith("h") and len(element.name) == 2:
            level = int(element.name[1])
            text = element.get_text().strip()
            markdown += f"\n{'#' * level} {text}\n\n"

        # Paragraphs
        elif element.name == "p":
            # Check for images inside the paragraph
            img = element.find("img")
            if img:
                alt_text = img.get("alt", "Image")
                src = img.get("src", "")
                markdown += f"![{alt_text}]({src})\n\n"

            # Process text content
            text = self._process_inline_elements(element)
            markdown += f"{text}\n\n"

        # Images
        elif element.name == "img":
            alt_text = element.get("alt", "Image")
            src = element.get("src", "")
            markdown += f"![{alt_text}]({src})\n\n"

        # Code blocks
        elif element.name == "pre":
            code_text = element.get_text().strip()
            markdown += f"```\n{code_text}\n```\n\n"

        # Tables
        elif element.name == "table":
            table_md = self._convert_table(element)
            markdown += table_md

        # Lists
        elif element.name == "ul":
            list_md = self._convert_list(element, ordered=False)
            markdown += list_md
        elif element.name == "ol":
            list_md = self._convert_list(element, ordered=True)
            markdown += list_md

        # Divs and other container elements
        elif element.name == "div":
            # Special handling for card/note blocks
            if "card" in element.get("class", []):
                card_content = element.find("div", {"class": "card-body"})
                if card_content:
                    note_text = self._process_inline_elements(card_content)
                    markdown += f"> **Note:** {note_text}\n\n"
                return markdown

            # Process all elements inside divs
            for nested_element in element.find_all(
                [
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "p",
                    "img",
                    "pre",
                    "table",
                    "ul",
                    "ol",
                ],
                recursive=False,
            ):
                markdown += self._process_element(nested_element)

            # If div has direct text content not in other elements
            direct_text = "".join(
                child
                for child in element.children
                if isinstance(child, str) and child.strip()
            )
            if direct_text:
                markdown += f"{direct_text}\n\n"

        return markdown

    def _clean_markdown(self, markdown):
        """Clean up the markdown by removing excessive newlines and fixing other issues."""
        import re

        # Replace 3+ consecutive newlines with 2 newlines
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)

        # Remove duplicate identical consecutive lines
        lines = markdown.split("\n")
        result = []
        prev_line = None

        for line in lines:
            # Skip duplicating identical lines
            if line.strip() and prev_line and line.strip() == prev_line.strip():
                continue
            result.append(line)
            prev_line = line

        return "\n".join(result)

    def _process_inline_elements(self, element) -> str:
        """
        Process inline formatting elements within a paragraph or block.
        """
        text = ""
        for child in element.children:
            if child.name is None:  # Plain text
                text += child.string or ""
            elif child.name == "strong" or child.name == "b":
                text += f"**{child.get_text()}**"
            elif child.name == "em" or child.name == "i":
                text += f"*{child.get_text()}*"
            elif child.name == "code":
                text += f"`{child.get_text()}`"
            elif child.name == "a":
                href = child.get("href", "")
                text += f"[{child.get_text()}]({href})"
            elif child.name == "br":
                text += "\n"
            else:
                # Recursively process other inline elements
                text += child.get_text()
        return text

    def _convert_table(self, table_element) -> str:
        """
        Convert HTML table to Markdown table format.
        """
        markdown_table = ""

        # Extract header row
        headers = []
        header_row = table_element.find("thead")
        if header_row:
            for th in header_row.find_all("th"):
                headers.append(th.get_text().strip())

        # Create header row
        if headers:
            markdown_table += "| " + " | ".join(headers) + " |\n"
            markdown_table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        # Process body rows
        body = table_element.find("tbody")
        if body:
            for tr in body.find_all("tr"):
                row_cells = []
                for td in tr.find_all("td"):
                    row_cells.append(td.get_text().strip())
                markdown_table += "| " + " | ".join(row_cells) + " |\n"

        return markdown_table + "\n"

    def _convert_list(self, list_element, ordered=False) -> str:
        """
        Convert HTML lists to Markdown format.
        """
        markdown_list = ""
        for i, li in enumerate(list_element.find_all("li", recursive=False)):
            prefix = f"{i+1}. " if ordered else "- "
            markdown_list += f"{prefix}{li.get_text().strip()}\n"

        return markdown_list + "\n"

    def save_content(self, title: str, content: str) -> Path:
        """
        Save content to a Markdown file.

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
            # Convert HTML to Markdown
            markdown_content = self.convert_content(title, content)

            # Create file name with index and title
            file_name = f"{self.index:03d}_{sanitize_filename(title)}"

            # Create output file
            output_file = Path(f"{file_name}.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Content saved: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving content: {e}")
            return Path()
