# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import requests
# import re
# import csv
# from urllib.parse import urlparse
# import requests
# from bs4 import BeautifulSoup
# import re
# import csv
# import together
# import argparse  # Assuming Together API has a Python client
# import sqlite3
#
# parser = argparse.ArgumentParser(description="Scrape Shopify URLs and process products.")
# parser.add_argument("--niche", required=True, help="Niche/category of the products.")
# parser.add_argument("--city", required=True, help="City to target in the search.")
# parser.add_argument("--country", required=True, help="Country to target in the search.")
#
# # Parse arguments
# args = parser.parse_args()
# niche = args.niche
# city = args.city
# country = args.country
# # Configure Selenium WebDriver
# options = webdriver.ChromeOptions()
# options.add_argument("--disable-extensions")
# options.add_argument("--disable-gpu")
# options.add_argument("--hide-scrollbars")
# options.add_argument("--no-sandbox")
# options.add_argument('--headless')  # Run in headless mode
# options.add_argument("--ignore-certificate-errors")
# options.add_argument("--disable-session-crashed-bubble")
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
# options.add_argument("--disable-blink-features=AutomationControlled")
#
# chrome_driver_path = r'c:\Program Files (x86)\chromedriver-win64\chromedriver.exe'
# # Initialize the WebDriver
# driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)
#
# urls = []
#
# # Step 1: Scrape URLs using Selenium
# try:
#     driver.get('https://www.google.com')
#     search_box = driver.find_element(By.NAME, "q")
#     search_query = f'inurl:myshopify.com {niche} in {city},{country}'
#     search_box.send_keys(search_query)
#     search_box.send_keys(Keys.RETURN)
#     time.sleep(2)
#
#     # Extract URLs from search results
#     links = driver.find_elements(By.CSS_SELECTOR, "a")
#     for link in links:
#         url = link.get_attribute("href")
#         if url and "myshopify.com/" in url:
#             urls.append(url)
#
#     driver.quit()
#
#     urls = list(set(urls))  # Remove duplicates
#
# finally:
#     driver.quit()
#
# processed_urls = []
# for url in urls:
#     parsed_url = urlparse(url)  # Parse the URL
#     domain = f"{parsed_url.scheme}://{parsed_url.netloc}"  # Extract scheme and domain
#     sitemap_url = f"{domain}/sitemap.xml"  # Add /sitemap.xml
#     processed_urls.append(sitemap_url)
#
# # Output: List of processed URLs
# print(processed_urls)
#
#
# def initialize_db(db_name="scraped_data.db"):
#     conn = sqlite3.connect(db_name)
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS products (
#             url TEXT,
#             title TEXT,
#             description TEXT,
#             image_url TEXT,
#             price TEXT,
#             city TEXT,
#             country TEXT,
#             niche TEXT
#         )
#     ''')
#     conn.commit()
#     return conn
#
#
# def save_to_db(data, conn):
#     cursor = conn.cursor()
#     for item in data:
#         cursor.execute('''
#             INSERT INTO products (url, title, description, image_url, price, city, country, niche)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (item['url'], item['title'], item['description'], item['image_url'], item['price'], item['city'],
#               item['country'], item['niche']))
#     conn.commit()
#
#
# def generate_product_price(product_title, product_description, country_name, city_name, niche, api_key):
#     """
#     Generate the price of a product using Together AI, based on the product's title, description, country, city, and niche.
#
#     Args:
#         product_title (str): The title of the product.
#         product_description (str): The description of the product.
#         country_name (str): The country where the product is located.
#         city_name (str): The city where the product is located.
#         niche (str): The niche or category of the product.
#         api_key (str): API key for Together AI.
#
#     Returns:
#         str: The price of the product with the currency symbol, or an error message.
#     """
#     try:
#         # Initialize Together AI client
#         client = together.Client(api_key=api_key)
#
#         # Define the prompt
#         prompt = (
#             "You are a pricing expert. Based on the following details, provide the expected price of the product "
#             "ONLY as a number followed by the currency sign. Do not include any extra text or words.\n\n"
#             "Product Title: {product_title}\n"
#             "Product Description: {product_description}\n"
#             "Country: {country_name}\n"
#             "City: {city_name}\n"
#             "Niche: {niche}\n\n"
#             "What is the expected price of the product?"
#         )
#
#         # Format the prompt with the provided inputs
#         prompt = prompt.format(
#             product_title=product_title,
#             product_description=product_description,
#             country_name=country_name,
#             city_name=city_name,
#             niche=niche
#         )
#
#         # Send the request
#         response = client.chat.completions.create(
#             model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=10,  # Sufficient to get a price with currency
#             temperature=0.2  # Low temperature to reduce variability
#         )
#
#         # Extract the response content
#         price = response.choices[0].message.content.strip()
#
#         # Ensure the response is clean (e.g., no quotes or extra spaces)
#         price = price.replace('"', '').replace(' ', '')
#
#         return price
#
#     except Exception as e:
#         print(f"Error generating price with Together AI: {e}")
#         return None
#
#
# # Function to fetch and parse XML sitemap
# def fetch_sitemap(url):
#     try:
#         response = requests.get(url, timeout=10)
#         if response.status_code == 200:
#             return BeautifulSoup(response.content, "xml")
#         else:
#             print(f"Failed to fetch sitemap: {url} (Status Code: {response.status_code})")
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching sitemap: {url} - {e}")
#     return None
#
#
# # Function to extract product details from a product page
# def scrape_product_details(product_url):
#     product_data = {
#         "url": product_url,
#         "title": None,
#         "description": None,
#         "image_url": None,
#         "price": None,
#         "city": city,
#         "country": country,
#         "niche": niche
#     }
#     try:
#         response = requests.get(product_url, timeout=10)
#         if response.status_code == 200:
#             html = response.text
#             soup = BeautifulSoup(html, "html.parser")
#             product_data["title"] = soup.find("title").text if soup.find("title") else None
#             meta_description = soup.find("meta", attrs={"name": "description"})
#             product_data["description"] = meta_description["content"] if meta_description else None
#             product_data['price'] = generate_product_price(product_data["title"], product_data["description"], country,
#                                                            city, niche,
#                                                            "8e20cf957a59cbfa992c3587d9f684ee0b7209e5b00ac4be07ecce36c0cdf92c")
#         else:
#             print(f"Failed to fetch product page: {product_url} (Status Code: {response.status_code})")
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching product details for {product_url}: {e}")
#     return product_data
#
#
# # Function to process product sitemaps
# def process_product_sitemap(sitemap_url):
#     product_details = []
#     sitemap = fetch_sitemap(sitemap_url)
#     if sitemap:
#         url_tags = sitemap.find_all("url")  # Get all URL tags from the sitemap
#         total_urls = len(url_tags)  # Total number of URLs to process
#         if total_urls == 0:
#             print("No URLs found in the sitemap.")
#             return product_details
#
#         for index, url_tag in enumerate(url_tags):
#             try:
#                 product_url = url_tag.find("loc").text
#                 image_url = url_tag.find("image:loc").text if url_tag.find("image:loc") else None
#                 if image_url:  # Only proceed if image_url is present
#                     product_data = scrape_product_details(product_url)
#                     product_data["image_url"] = image_url
#                     product_details.append(product_data)
#
#                 # Print the current progress
#                 percentage_done = (index + 1) / total_urls * 100
#                 print(f"Processed {index + 1}/{total_urls} URLs ({percentage_done:.2f}% completed).")
#             except Exception as e:
#                 print(f"Error processing product URL: {e}")
#
#     return product_details
#
#
# # Main function to process multiple sitemaps
# def main(sitemap_urls):
#     conn = initialize_db()
#     all_product_details = []
#     total_sitemaps = len(sitemap_urls)
#     start_time = time.time()
#
#     for idx, sitemap_url in enumerate(sitemap_urls):
#         remaining_sitemaps = total_sitemaps - idx
#         print(
#             f"Processing parent sitemap: {sitemap_url} ({idx + 1}/{total_sitemaps}). {remaining_sitemaps} sitemaps left.")
#         parent_sitemap = fetch_sitemap(sitemap_url)
#         if parent_sitemap:
#             product_sitemaps = [sitemap.find("loc").text for sitemap in parent_sitemap.find_all("sitemap") if
#                                 "products" in sitemap.find("loc").text]
#             total_urls = len(product_sitemaps)
#             for url_idx, product_sitemap_url in enumerate(product_sitemaps):
#                 remaining_urls = total_urls - url_idx
#                 print(
#                     f"Processing product sitemap: {product_sitemap_url} ({url_idx + 1}/{total_urls}). {remaining_urls} URLs left.")
#                 all_product_details.extend(process_product_sitemap(product_sitemap_url))
#
#                 # Time estimate
#                 elapsed_time = time.time() - start_time
#                 avg_time_per_url = elapsed_time / (idx * total_urls + url_idx + 1)
#                 estimated_time_left = avg_time_per_url * (
#                             total_sitemaps * total_urls - (idx * total_urls + url_idx + 1))
#                 print(f"Estimated time left: {estimated_time_left:.2f} seconds.")
#         else:
#             print(f"Skipping {sitemap_url} as it did not return a valid response.")
#         print(f"Completed {sitemap_url}. {remaining_sitemaps - 1} sitemaps left.")
#
#     save_to_db(all_product_details, conn)
#     conn.close()
#     total_time = time.time() - start_time
#     print(f"All sitemaps processed. Total time: {total_time:.2f} seconds.")
#
# 
# # Example: List of multiple sitemap URLs
# sitemap_urls = processed_urls
#
# if __name__ == "__main__":
#     main(sitemap_urls)
#
