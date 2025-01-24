from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re

# Mappings of target certification alt properties to preferred sheet names
CERTIFICATIONS = {
    "FERPA Certified": "FERPA",
    "COPPA Safe Harbor": "COPPA",
    "California Student Privacy Certified": "CSPC",
    "ATLIS Certified": "ATLIS"
}


def scrape_page(driver, product_data, prods_w_subs):
    """
    Scrapes individual pages, looping through each product div and sub-products to pull data & update Dataframe.
    Attributes scraped:
        -Product Name
        -Company Name
        -Website
        -Certifications
        -Sub Products
    :param driver: Chrome driver with iKeepSafe website endpoint with product list
    :param product_data: Dict of product data pulled from website
    """

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # All products listed in product__grid div
    products_grid = soup.find('div', class_='products__grid')
    if not products_grid:
        raise Exception("No products found on the page.")

    prod_count = 0  # For logging purposes

    for product in products_grid.find_all('div', recursive=False):

        name_h4_span = product.find('span', class_='h4')  # Product name in span class h4
        comp_h5_div = product.find('div', class_='h5')  # Product name in div class h5
        product_name = name_h4_span.get_text(strip=True) if name_h4_span else None
        product_company = comp_h5_div.get_text(strip=True) if comp_h5_div else None

        if product_company and not product_name:
            raise Exception("Missing Product Name for Company: "+product_company)

        if product_name:

            # Extract product ID from class tag attribute, which is only in parent products
            product_classes = product.get("class", [])
            product_id = None  # Default to None if no ID found
            # Search for a class matching the pattern "product--<digits>"
            for cls in product_classes:
                match = re.match(r"product--(\d+)", cls)
                if match:
                    product_id = int(match.group(1))  # Extract the numeric ID
                    break

            # Initialize certification columns
            cert_flags = {cert: False for cert in CERTIFICATIONS.values()}

            cert_div = product.find('div', class_='product__certs')  # Certs in <div class="product__certs">
            if not cert_div:
                raise Exception("Product listed with no certifications: "+product_name)
            for cert_img in cert_div.find_all('img'):  # Certs listed as images; text is in alt attribute
                cert_alt = cert_img.get('alt', '').strip()
                if cert_alt in CERTIFICATIONS:
                    cert_flags[CERTIFICATIONS[cert_alt]] = True
                else:
                    raise Exception(f"Unknown cert, {cert_alt}, for {product_name}.")

            # Parent product website is listed in different divs depending on the existence of sub-products.
            # If sub-products exist, parent product website is in product__companyFooter. Else, in product__footer
            main_product_link = None
            # Check if sub-products exist
            subproducts_div = product.find('div', class_='product__subproducts')
            if subproducts_div:
                prods_w_subs.append(product_name)  # For logging purposes

                # Extract main product "View Website" link from div specific to sub-products
                company_footer = product.find('div', class_='product__companyFooter')
                if company_footer:
                    link_element = company_footer.find('a', string="View Website")
                    if link_element and link_element.get('href'):
                        main_product_link = link_element['href']
                else:
                    raise Exception("Existing sub-products without product__companyFooter div: "+product_name)

                # Loop through sub-products, which are in list tags
                for subproduct in subproducts_div.find_all('li'):
                    subproduct_name_div = subproduct.find('div')  # Sub-product names in naked div tag within list
                    subproduct_name = subproduct_name_div.get_text(strip=True) if subproduct_name_div else None

                    if not subproduct_name:
                        raise Exception("Missing sub-product name in list for main product: "+product_name)

                    subproduct_link = main_product_link  # Default to parent link, if no sub link found.
                    # Check for sub-product "View Website" link
                    # Sub link View Website text has additional arrow icons. Use contains logic rather than exact match.
                    sub_link_element = subproduct.find('a')
                    if sub_link_element and "View Website" in sub_link_element.text:
                        subproduct_link = sub_link_element['href']

                    # Add sub-product data
                    product_data.append({
                        "IKS ID": product_id,
                        "Product Name": subproduct_name,
                        "Product Company": product_company,
                        "Website": subproduct_link,
                        **cert_flags
                    })

                    prod_count += 1
            else:
                # Extract main product "View Website" link
                footer = product.find('div', class_='product__footer')
                if footer:
                    link_element = footer.find('a', string="View Website")
                    if link_element and link_element.get('href'):
                        main_product_link = link_element['href']
                else:
                    raise Exception("No subproducts with no product__footer div: "+product_name)

            # Add data to the DataFrame
            product_data.append({
                "IKS ID": product_id,
                "Product Name": product_name,
                "Product Company": product_company,
                "Website": main_product_link,
                **cert_flags
            })

            prod_count += 1

    return prod_count


def connect_ikeepsafe():
    """
    Connects to ikeepsafe website for product certs. Flips through pages to be scraped.
    :return: scraped product data
    """

    try:
        # set up Chrome and Selenium
        driver = webdriver.Chrome()
        driver.get('https://ikeepsafe.org/products/#all')

        product_data = []
        prods_w_subs = []
        last_page_number = None
        prod_total = 0

        while True:
            # scrape page, return product count to add to total count
            prod_total += scrape_page(driver, product_data, prods_w_subs)

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
            time.sleep(1)  # Wait for the page to load; adjust timing as needed

        driver.quit()

        print("Product Count: ", prod_total)
        print("Products containing sub-products", prods_w_subs)

        return product_data

    except Exception as e:
        driver.quit()
        print("connect_ikeepsafe() exception block")
        print("Product Count: ", prod_total)
        print("Products containing sub-products", prods_w_subs)
        raise
