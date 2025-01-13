from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import traceback

# List of target certification alt properties
CERTIFICATIONS = {
    "FERPA Certified": "FERPA",
    "COPPA Safe Harbor": "COPPA",
    "California Student Privacy Certified": "CSPC",
    "ATLIS Certified": "ATLIS"
}


def scrape_page(driver, product_data):
    """
    Scrapes individual pages, looping through each product div to pull data & update Dataframe
    :param driver: Chrome driver with iKeepSafe website endpoint with product list
    :param product_data: Dict of product data pulled from website
    """

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # All products listed in product__gric div
    products_grid = soup.find('div', class_='products__grid')

    if not products_grid:
        raise Exception("No products found on the page.")

    prod_count = 0
    for product in products_grid.find_all('div', recursive=False):

        h4_span = product.find('span', class_='h4')  # Product name in span class h4
        h5_class = product.find('div', class_='h5')  # Product name in div class h5
        product_name = h4_span.get_text(strip=True) if h4_span else None
        product_company = h5_class.get_text(strip=True) if h5_class else None

        if product_name or product_company:

            # Extract "View Website" link
            website_link = None
            view_website_element = product.find('a', string="View Website")
            if view_website_element and view_website_element.get('href'):
                website_link = view_website_element['href']

            # Initialize certification flags
            cert_flags = {cert: False for cert in CERTIFICATIONS.values()}

            # Find certifications in <div class="product__certs">
            cert_div = product.find('div', class_='product__certs')

            if not cert_div:
                raise Exception("Product listed with no certifications.")

            if cert_div:
                for cert_img in cert_div.find_all('img'):
                    cert_alt = cert_img.get('alt', '').strip()
                    if cert_alt in CERTIFICATIONS:
                        cert_flags[CERTIFICATIONS[cert_alt]] = True

            # Add data to the DataFrame
            product_data.append({
                "Product Name": product_name,
                "Product Company": product_company,
                "Website": website_link,
                **cert_flags
            })

            prod_count += 1

    return prod_count


def main():
    """
    Scrapes iKeepSafe for product certifications, spanning multiple pages.
    TODO: Realized there are also subproducts on some of the products (see GoGuardian & ExploreLearning) that need to also be looped through
    :return:
    """
    # set up Chrome and Selenium
    driver = webdriver.Chrome()
    driver.get('https://ikeepsafe.org/products/#all')

    product_data = []
    last_page_number = None
    prod_total = 0

    while True:
        try:
            # scrape page, return product count to add to total count
            prod_total += scrape_page(driver, product_data)

            current_page_number = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.products__pagination__item--active"))
            ).text.strip()

            if current_page_number == last_page_number:
                print("Reached the last page or stuck on a page:", current_page_number)
                break
            last_page_number = current_page_number

            # Check if the "Next" button exists
            next_button_exists = len(driver.find_elements(By.CSS_SELECTOR,
                                                          "a.products__pagination__item.product__pagination__item--nav i.fa.fa-arrow-right")) > 0
            if not next_button_exists:
                print("Next button no longer exists. Last page reached:", current_page_number)
                break

            # Navigate to next page
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "a.products__pagination__item.product__pagination__item--nav i.fa.fa-arrow-right"))
            )

            # Check if the next button is the last element or disabled (some websites use this)
            if "disabled" in next_button.get_attribute("class"):
                print("Next button is disabled. Last page reached:", current_page_number)
                break

            next_button.click()
            time.sleep(2)  # Wait for the page to load; adjust timing as needed
        except Exception as e:
            print(traceback.format_exc())
            break

    driver.quit()
    print("Product Count: ", prod_total)

    # Convert the product data to a Pandas DataFrame
    df = pd.DataFrame(product_data)
    print(df)
    print("Dataframe Row Count", len(df))


# Run the function
main()
