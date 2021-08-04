from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from constants import CHROME_DRIVER, HIDE_BROWSER, PRODUCTS_PER_PAGE, MAX_PROD_PER_ITEM
import pandas as pd
import numpy as np
import time


class AmazonBot(object):
    def __init__(self, items):
        # Items that need to be searched for
        self.items = items
        # Amazon homepage url
        self.amazon_url = "https://www.amazon.sg/"
        # Create options of the driver
        options = Options()
        options.headless = HIDE_BROWSER  # True: hides brwoser when code runs
        # Last window of browser remains open (allows easier troubleshooting if required)
        options.add_experimental_option("detach", True)

        #Driver ()
        self.driver = webdriver.Chrome(CHROME_DRIVER, options=options)
        # Where data is stored
        self.data = {}
        # Go to Amazon's url
        self.driver.get(self.amazon_url)

    def search_items(self):
        for item in self.items:
            item_data = {'names': [], 'urls': [], 'prices': [],
                         'seller_names': [], 'ratings': []}
            count = 0  # No. of products of that item that have been retrieved for current page
            page = 1  # Page no.
            # After how many items of  apage to move on to next page
            page_increment = PRODUCTS_PER_PAGE
            max_retrieves = MAX_PROD_PER_ITEM  # Max number of products per item to retrieve
            print(f"Searching for {item}.....")

            while page*page_increment <= max_retrieves:
                self.driver.get(self.amazon_url +
                                f"s?k={item.replace(' ','+')}&page={page}")
                results = self.driver.find_elements_by_xpath(
                    '//div[@data-uuid][@data-index]')
                asins = []
                for result in results:
                    asins.append(result.get_attribute("data-asin"))
                for asin in asins:
                    if count >= page_increment:
                        count = 0
                        page += 1
                        break
                    # Url of product
                    url = self.amazon_url + 'dp/' + asin
                    # Get product data
                    price, name, seller, rating = self.get_data(url)

                    # Add data to dictionary of the item
                    item_data['prices'] += [price]
                    item_data['urls'] += [url]
                    item_data['names'] += [name]
                    item_data['seller_names'] += [seller]
                    item_data['ratings'] += [rating]

                    # Add item data to entire data
                    self.data[item] = item_data
                    # Increment count
                    count += 1
                    time.sleep(1)
                print(f"Page {page-1} done")

        return self.data

    def get_product_price(self):
        # Find the price
        try:
            product_price = self.driver.find_element_by_id(
                "priceblock_ourprice").text
        except:
            # Price is stored under this id if a deal is applicable
            try:
                product_price = self.driver.find_element_by_id(
                    "priceblock_dealprice").text
            except:
                product_price = "Not available"
        return product_price

    def get_product_name(self):
        try:
            product_name = self.driver.find_element_by_id("productTitle").text
        except:
            product_name = "Not available"
        return product_name

    def get_product_seller(self):
        try:
            seller_name = self.driver.find_element_by_id("bylineInfo").text
        except:
            seller_name = "Not available"
        return seller_name

    def get_product_rating(self):
        try:
            product_rating = self.driver.find_element_by_xpath(
                '//*[@id="acrPopover"]/span[1]/a/i[1]/span').get_attribute("innerText")
        except:
            product_rating = "Not available"

        return product_rating

    def get_data(self, url):
        # Go to product url
        self.driver.get(url)
        # Extract the data using the defined methods
        price = self.get_product_price()
        name = self.get_product_name()
        seller = self.get_product_seller()
        rating = self.get_product_rating()
        return price, name, seller, rating

    # output data in excel format with the items represented as different sheets
    def generate_excel(self):
        writer = pd.ExcelWriter("data.xlsx", engine='xlsxwriter')
        for item, item_data in self.data.items():
            # Make data into datafram for the item
            df = pd.DataFrame(item_data)
            # Change 0 based indexing to 1-based indexing
            df.index = np.arange(1, len(df) + 1)
            # Write to excel file with item name as the sheet name
            df.to_excel(writer, sheet_name=item)
        # Save excel file
        writer.save()
