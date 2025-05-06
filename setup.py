#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="HTB-AcadSaver",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "requests>=2.24.0",
        "pyyaml>=5.3.1",
    ],
    entry_points={
        "console_scripts": [
            "htb-scraper=scraper.main:run",
        ],
    },
    author="Ghøstkeed",
    description="A specialized scraper for HackTheBox Academy modules that recursively collects chapters and saves them in Markdown format for offline reference",
    long_description="This tool helps HackTheBox Academy users archive their course materials by scraping module content and saving it in a structured Markdown format. It traverses all chapters within a module recursively, preserving the course structure and content for offline access and reference.",
    keywords="hackthebox, academy, scraper, cybersecurity, training, markdown, educational",
    python_requires=">=3.6",
)