import random
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import json
from typing import Dict, List


class UnitedAirlinesScraper:
    def __init__(self, proxy_file):
        self.base_url = 'https://united.com/en/gb'

        # Large set of User-Agents to simulate various devices and browsers
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/90.0.818.66 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:78.0) Gecko/20100101 Firefox/78.0'
        ]

        # Screen resolutions for various devices
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
            {'width': 1280, 'height': 720},
            {'width': 1600, 'height': 900}
        ]

        self.timezones = ['Europe/London', 'Europe/Paris', 'America/New_York']
        self.locales = ['en-GB', 'en-US', 'en-CA']
        self.proxies = self.load_proxies(proxy_file)

        # List of potential cities for departure and arrival
        self.cities = [
            "London", "New York, NY", "San Francisco, CA", "Chicago, IL", "Los Angeles, CA",
            "Houston, TX", "Miami, FL", "Toronto, ON", "Paris", "Berlin", "Amsterdam", "Tokyo",
            "Dubai", "Sydney", "Singapore"
        ]

    def load_proxies(self, proxy_file):
        """Load proxies from the specified file."""
        with open(proxy_file, 'r') as file:
            proxies = [line.strip() for line in file.readlines()]
        return proxies

    def parse_proxy(self, proxy_str):
        ip, port, username, password = proxy_str.split(':')
        return {
            'server': f'http://{ip}:{port}',
            'username': username,
            'password': password
        }

    def setup_browser(self, playwright):
        # Select a random proxy
        proxy_str = random.choice(self.proxies)
        proxy = self.parse_proxy(proxy_str)

        browser = playwright.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-features=IsolateOrigins',
                '--disable-automation',
                '--disable-infobars'
            ]
        )

        context = browser.new_context(
            viewport=random.choice(self.viewports),
            user_agent=random.choice(self.user_agents),
            locale=random.choice(self.locales),
            timezone_id=random.choice(self.timezones),
            proxy=proxy,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # Scripts to hide WebDriver traces
        context.add_init_script("""
               // Override navigator.webdriver
               Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

               // Override navigator's properties for better bot protection
               Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
               Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });

               // Other minor adjustments
               Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
               Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
               Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 1 });

               // Spoof user-agent specific properties
               window.outerWidth = screen.width;
               window.outerHeight = screen.height;
           """)

        return browser, context

    def random_hover(self, page, element, offset=5):
        """Simulate natural mouse hover with slight offset from the center."""
        box = element.bounding_box()
        if box is None:
            return  # Element not found, skip

        # Random offset for hover position
        x = box['x'] + box['width'] / 2 + random.uniform(-offset, offset)
        y = box['y'] + box['height'] / 2 + random.uniform(-offset, offset)

        # Hover near the element first, then move to the exact position
        page.mouse.move(x - offset, y - offset)
        time.sleep(random.uniform(0.1, 0.3))
        page.mouse.move(x, y)

    def fill_input_with_delay(self, input_element, text, delay_range=(0.1, 0.3), use_fill=True):
        """Emulate typing with delay and random hover before interaction."""
        self.random_hover(input_element.page, input_element)
        time.sleep(random.uniform(0.5, 1.5))
        input_element.click()
        if use_fill:
            input_element.fill(text)
        else:
            for char in text:
                input_element.type(char, delay=random.uniform(*delay_range) * 1000)

    def handle_interaction(self, element, delay_range=(0.5, 1.5)):
        """Hover, pause, then click with randomized delays."""
        self.random_hover(element.page, element)
        time.sleep(random.uniform(*delay_range))
        element.click()
        time.sleep(random.uniform(*delay_range))

    def fill_search_form(self, page, from_city: str, to_city: str, date: str) -> bool:
        try:
            # Select One-Way option
            one_way_button = page.locator('#radiofield-item-id-flightType-1')
            self.handle_interaction(one_way_button)

            # Enter origin city
            origin_input = page.locator('#bookFlightOriginInput')
            self.fill_input_with_delay(origin_input, from_city, use_fill=True)
            page.wait_for_selector('#autocomplete-item-0', state='visible', timeout=3000)
            page.keyboard.press('ArrowDown')
            page.keyboard.press('Enter')
            time.sleep(random.uniform(1, 2))

            # Enter destination city
            destination_input = page.locator('#bookFlightDestinationInput')
            self.fill_input_with_delay(destination_input, to_city, use_fill=True)
            page.wait_for_selector('#autocomplete-item-0', state='visible', timeout=3000)
            page.keyboard.press('ArrowDown')
            page.keyboard.press('Enter')
            time.sleep(random.uniform(1, 2))

            # Select date in the calendar
            self.select_date_in_calendar(page, datetime.strptime(date, "%Y-%m-%d"))
            time.sleep(random.uniform(1, 3))

            # Click the search button
            search_button = page.get_by_role("button", name="Find flights")
            self.handle_interaction(search_button)
            time.sleep(random.uniform(10, 15))
            return True

        except Exception as e:
            print(f"Error while filling search form: {e}")
            return False

    def select_date_in_calendar(self, page, target_date: datetime) -> bool:
        try:
            date_start_button = page.locator('#DepartDate_start')
            self.handle_interaction(date_start_button)

            while True:
                month_captions = page.locator('.CalendarMonth_caption:visible strong').all()
                visible_months = [datetime.strptime(caption.text_content(), '%B %Y') for caption in month_captions if
                                  caption.text_content()]

                if not visible_months:
                    print("Failed to find visible months")
                    return False

                earliest_visible = visible_months[0].replace(day=1)
                latest_visible = visible_months[-1].replace(day=28) + timedelta(days=4)
                latest_visible = latest_visible.replace(day=1) - timedelta(days=1)

                if earliest_visible <= target_date <= latest_visible:
                    target_day_label = target_date.strftime('%A, %d %B %Y')
                    day_selector = f'.CalendarDay[aria-label*="{target_day_label}"]'
                    day_element = page.locator(day_selector)
                    if day_element.is_visible():
                        self.handle_interaction(day_element)
                        print(f"Selected date: {target_day_label}")
                        return True

                if target_date < earliest_visible:
                    prev_button = page.locator('.atm-c-datepicker__navigation.atm-c-datepicker-prev')
                    if prev_button.is_visible():
                        self.handle_interaction(prev_button)
                    else:
                        print("Back button not found")
                        return False
                else:
                    next_button = page.locator('.atm-c-datepicker__navigation.atm-c-datepicker-next')
                    if next_button.is_visible():
                        self.handle_interaction(next_button)
                    else:
                        print("Forward button not found")
                        return False

        except Exception as e:
            print(f"Error while selecting date: {e}")
            return False

    def scrape_flights(self) -> List[Dict]:
        from_city = random.choice(self.cities)
        to_city = random.choice([city for city in self.cities if city != from_city])

        start_date = datetime.now() + timedelta(days=90)
        end_date = datetime.now() + timedelta(days=180)
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        date_str = random_date.strftime("%Y-%m-%d")

        with sync_playwright() as playwright:
            browser, context = self.setup_browser(playwright)
            page = context.new_page()

            try:
                page.goto(self.base_url)
                page.wait_for_load_state("networkidle")

                if not self.fill_search_form(page, from_city, to_city, date_str):
                    return []

                page.wait_for_selector('.app-components-Shopping-GridItem-styles__flightRow--QbVXL', timeout=30000)
                self.simulate_user_scroll(page)
                flight_elements = page.locator('.app-components-Shopping-GridItem-styles__flightRow--QbVXL').all()
                flights_data = []
                for flight in flight_elements:
                    flight_data = {
                        'airline': flight.locator(
                            '.app-components-AriaMessage-styles__visuallyHidden--LBJnv').text_content(),
                        'price': flight.locator(
                            '.app-components-Shopping-PriceCard-styles__priceValueNonUS--c6Loz span').text_content(),
                    }
                    flights_data.append(flight_data)

                return flights_data

            except Exception as e:
                print(f"Error during scraping: {e}")
                return []

            finally:
                context.close()

    def simulate_user_scroll(self, page):
        for _ in range(5):
            page.mouse.wheel(0, random.randint(200, 600))
            time.sleep(random.uniform(2, 5))


if __name__ == "__main__":
    proxy_file = 'proxies.txt'
    scraper = UnitedAirlinesScraper(proxy_file)
    flights = scraper.scrape_flights()

    if flights:
        print("\nFlights found:")
        print(json.dumps(flights, indent=2, ensure_ascii=False))
    else:
        print("\nNo flights found or an error occurred.")
