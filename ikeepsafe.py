from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import traceback


def scrape_page(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    products_grid = soup.find('div', class_='products__grid')

    prod_count = 0
    if products_grid:
        for product in products_grid.find_all('div', recursive=False):
            # Product name is in span with class="h4"
            h4_span = product.find('span', class_='h4')

            if h4_span:
                h4_text = h4_span.get_text(strip=True)
                print(h4_text)
                prod_count += 1

    else:
        print("No products found on the page.")

    return prod_count


def main():
    """
    Scrapes iKeepSafe for product certifications, spanning multiple pages.
    TODO: Realized there are also subproducts on some of the products (see GoGuardian & ExploreLearning) that need to also be looped through
    TODO: Loop through individual cert page links & copy to google sheets. Currently manually changing # at the end of url per certification type
    :return:
    """
    # set up Chrome and Selenium
    driver = webdriver.Chrome()
    driver.get('https://ikeepsafe.org/products/#all')

    last_page_number = None
    prod_total = 0

    while True:
        try:
            # scrape page, return product count to add to total count
            prod_total += scrape_page(driver)

            current_page_number = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.products__pagination__item--active"))
            ).text.strip()

            print(current_page_number)
            print(last_page_number)

            if current_page_number == last_page_number:
                print("Reached the last page or stuck on a page.")
                break
            last_page_number = current_page_number

            # Check if the "Next" button exists
            next_button_exists = len(driver.find_elements(By.CSS_SELECTOR,
                                                          "a.products__pagination__item.product__pagination__item--nav i.fa.fa-arrow-right")) > 0
            if next_button_exists:
                # Navigate to next page
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                "a.products__pagination__item.product__pagination__item--nav i.fa.fa-arrow-right"))
                )

                # Check if the next button is the last element or disabled (some websites use this)
                if "disabled" in next_button.get_attribute("class"):
                    print("Next button is disabled. Last page reached.")
                    break

                next_button.click()
                time.sleep(2)  # Wait for the page to load; adjust timing as needed
            else:
                print("Next button no longer exists; End of pages:", current_page_number)
                break
        except Exception as e:
            print(traceback.format_exc())
            break

    driver.quit()
    print("Product Total: ", prod_total)


# Run the function
main()
