# HTB Academy Scraper

A specialized tool for downloading and archiving HackTheBox Academy modules for offline reference. This scraper recursively collects all chapters within a module and saves them in a structured Markdown format.

## Features

- **Module Archiving**: Save entire HackTheBox Academy modules as Markdown files
- **Recursive Scraping**: Automatically collects all chapters within a module
- **Structured Output**: Maintains the original structure of courses for easy navigation
- **Configuration Based**: Easy to configure through a simple YAML file
- **Clean Output Format**: Content is saved in Markdown for easy reading and reference

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Oxooi/htb-academy-scraper.git
   cd htb-academy-scraper
   ```

2. Install the package:
   ```bash
   pip install .
   ```

   Or install in development mode:
   ```bash
   pip install -e .
   ```

3. Configure your settings:
   ```bash
   # Copy the example config
   cp scraper/config/config.example.yaml scraper/config/config.yaml
   
   # Edit the config file with your details
   # You need to add your HackTheBox Academy cookies and the starting URL
   nano scraper/config/config.yaml
   ```

## Configuration

Edit `scraper/config/config.yaml` with your settings:

```yaml
# The starting URL of the module you want to scrape
url: "https://academy.hackthebox.com/module/xxx/section/xxx"

# The file to temporarily store links (will be deleted after scraping)
file: "links.txt"

# Your HackTheBox Academy cookies (required for authentication)
cookies:
  htb_academy_session: "your_session_cookie_value"
```

### How to get your cookies

1. Log in to HackTheBox Academy in your browser
2. Open Developer Tools (F12)
3. Go to the Application tab
4. Under Storage, select Cookies
5. Copy the cookie values for the academy.hackthebox.com domain

## Usage

After installation, you can run the scraper using:

### Linux
```bash
htb-scraper
```

### Windows
```bash
python -m scraper
```

The content will be saved in a `results` directory, organized by module title.

## Directory Structure

```
results/
└── Module Title/
    ├── 001_Chapter_Title/
    │   └── 001_Chapter_Title.md
    ├── 002_Chapter_Title/
    │   └── 002_Chapter_Title.md
    └── ...
```

## Notes

- This tool is intended for personal, educational use only
- Please respect HackTheBox's terms of service
- The scraper requires a valid HackTheBox Academy account and cookies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for educational purposes only. The authors are not responsible for any misuse of this software or violations of HackTheBox's terms of service.