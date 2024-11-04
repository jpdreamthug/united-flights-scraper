# Flight Scraper

This project includes two scripts for scraping flight information from United Airlines:

1. **scraper.py** — a script using `Playwright`
2. **selenium-undetected-chrome.py** — a script using `Selenium` with `undetected-chromedriver`

## Script Overview

### scraper.py (Playwright)

This script leverages `Playwright` to automate the browser and scrape flight data from United Airlines, as implemented in the `scraper.py` file.

#### Playwright Limitations

During development, it was discovered that United Airlines detects Playwright as a WebDriver, leading to a redirect to an error page (HTTP 403). Consequently, Playwright cannot retrieve the flight data directly from the site.

#### Proxy Usage

To use `Playwright` with proxies, create a `proxies.txt` file to specify a list of proxies. Each proxy should be listed in the following format:

`ip:port:username:password`

Each line should represent a separate proxy. These proxies are used to mask the IP address when accessing the site.

### selenium-undetected-chrome.py (Selenium)

This script uses `Selenium` combined with `undetected-chromedriver`, which bypasses anti-bot detection and successfully retrieves flight information. The scraping logic is implemented in `selenium-undetected-chrome.py`.

#### Advantages of Using `undetected-chromedriver`

By using `undetected-chromedriver`, the Selenium script avoids detection as an automated browser, allowing it to successfully load and scrape data from United Airlines without triggering a 403 error.

## Installation and Usage

### Requirements

To run the scripts, the following libraries are required:

- `Playwright` and `Playwright-Stealth` for `scraper.py`
- `Selenium` and `undetected-chromedriver` for `selenium-undetected-chrome.py`

Create venv and install the dependencies by running the following command:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
## Running the Scripts

### scraper.py (Playwright)

Prepare a proxies.txt file with proxies in the specified format.

### Run the scraper.py script:

```bash
python scraper.py
```
Note: It’s recommended to use high-quality proxies, as Playwright may still be detected even when using proxies.

### selenium-undetected-chrome.py (Selenium)
Run the selenium-undetected-chrome.py script to scrape data from United Airlines without the need for proxies.

```bash
python selenium-undetected-chrome.py
```

## Summary
**scraper.py** using Playwright can work with proxies but may still encounter limitations due to WebDriver detection on United Airlines.

**selenium-undetected-chrome.py** using undetected-chromedriver successfully bypasses detection and provides a reliable solution for scraping flight data.
These scripts provide a solution for collecting data from United Airlines, taking into account site restrictions and anti-bot detection measures.
