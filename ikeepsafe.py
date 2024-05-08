from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


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
    TODO: Loop through individual cert page links & copy to google sheets. Currently manually changing # at the end of url per certification type
    :return:
    """
    # set up Chrome and Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get('https://ikeepsafe.org/products/#atlis')

    current_page_number = 1
    prod_total = 0

    while True:
        # print("Page ", current_page_number)

        # scrape page, return product count to add to total count
        prod_total += scrape_page(driver)

        current_page_number += 1

        try:
            # Navigate to next page
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "a.products__pagination__item.product__pagination__item--nav i.fa.fa-arrow-right"))
            )
            next_button.click()
            time.sleep(2)  # Wait for the page to load; adjust timing as needed
        except Exception as e:
            # print("No more pages or error navigating:", e)
            print("No more pages or error navigating.")
            break

    driver.quit()
    print("Product Total: ", prod_total)


# Run the function
main()
