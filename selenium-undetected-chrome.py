import undetected_chromedriver as uc
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_flights(origin, destination, travel_date):

    # Construct the URL with search parameters
    url = f"https://www.united.com/en/gb/fsr/choose-flights?tt=1&st=bestmatches&d={travel_date}&clm=7&taxng=1&f={origin}&px=1&newHP=True&sc=7&tqp=R&t={destination}&idx=1&mm=0"

    options = uc.ChromeOptions()
    options.headless = False
    driver = uc.Chrome(options=options)

    try:
        print(f"Navigating to {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "app-components-Shopping-GridItem-styles__flightRow--QbVXL"))
            )
            print("Page loaded successfully.")
        except TimeoutException:
            print("Timeout waiting for the flight results to load.")
            return []

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            print("Page scrolled successfully.")
        except Exception as e:
            print(f"Error during page scroll: {e}")

        flights = []
        try:
            flight_elements = driver.find_elements(By.CSS_SELECTOR,
                                                   ".app-components-Shopping-GridItem-styles__flightRow--QbVXL")
            if not flight_elements:
                print("No flight elements found on the page.")
                return []
        except NoSuchElementException:
            print("Could not locate flight elements.")
            return []

        # Extract data from each flight element
        for flight in flight_elements:
            try:
                price = flight.find_element(By.CSS_SELECTOR,
                                            ".app-components-Shopping-PriceCard-styles__priceValueNonUS--c6Loz span").text
                all_text_flight = flight.find_elements(By.CSS_SELECTOR,
                                                       ".app-components-AriaMessage-styles__visuallyHidden--LBJnv")

                if len(all_text_flight) < 5:
                    print("Unexpected format in flight data, skipping this flight.")
                    continue

                flights.append({
                    "price": price,
                    "origin": all_text_flight[2].text,
                    "destination": all_text_flight[4].text,
                    "departure_time": all_text_flight[0].text,
                    "arrival_time": all_text_flight[1].text,
                    "duration": all_text_flight[3].text
                })
            except NoSuchElementException:
                print("Error: One of the expected elements is missing in the flight data.")
            except IndexError:
                print("Error: Unexpected number of elements in flight data.")
            except ElementNotInteractableException:
                print("Error: Element not interactable, possibly due to page structure changes.")
            except Exception as e:
                print(f"Unexpected error while processing flight data: {e}")

        print("Flight data scraped successfully.")
        return flights

    except TimeoutException:
        print("Timeout while loading the page. Please check your internet connection or the site status.")
        return []
    except Exception as e:
        print(f"Unexpected critical error: {e}")
        return []

    finally:
        driver.quit()
        print("Browser closed.")


# Example usage of the function
if __name__ == "__main__":
    origin = "LHR"  # Departure city or city code (e.g., London, LON, LHR)
    destination = "IAD"  # Destination city or city code (e.g., Tokyo, NRT, LMJ)
    travel_date = "2024-12-12"  # Travel date

    flights = scrape_flights(origin, destination, travel_date)
    if flights:
        for flight in flights:
            print(flight)
    else:
        print("No flights available or an error occurred.")
