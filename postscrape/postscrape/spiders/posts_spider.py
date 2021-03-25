import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from shutil import which
from scrapy.selector import Selector 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from pprint import pprint
from urllib.parse import urljoin
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


options = Options()
options.headless = True

class MyntraCrawl(scrapy.Spider):
    name = 'casual'
    start_urls = [
        'https://www.myntra.com/men-sports-shoes',
    ]

    def __init__(self):
         self.driver = webdriver.Chrome('/home/ratishankar/Downloads/chromedriver')
    
    def parse(self, response):
        try:
            self.driver.get(response.url)
            mount_root = Selector(text = self.driver.page_source)
            page_results = mount_root.xpath("//*[@class='results-base']")
            
            url_list = set(page_results.xpath("li[@class='product-base']//a/@href").getall())

            for each_url in url_list:
                url = urljoin(response.url, each_url)
                shoe_page = self.driver.get(url)
                self.driver.execute_script("window.scrollTo(0, 1080)")
                self.driver.find_element_by_xpath("//div[@class = 'index-showMoreText']").click()
                _mount_root =  Selector(text = self.driver.page_source)
                shoe_urls  = _mount_root.xpath("//*[@class='image-grid-container common-clearfix']").re(r'url\("([^\")]+)')
                row_keys = _mount_root.xpath("//*[@class = 'index-rowKey']/text()").getall()
                row_values = _mount_root.xpath("//*[@class = 'index-rowValue']/text()").getall()
                specifications = dict(zip(row_keys, row_values))
                yield {
                    'title' : _mount_root.xpath("//h1[@class='pdp-title']/text()").get(),
                    'name' :  _mount_root.xpath("//h1[@class='pdp-name']/text()").get(),
                    'url' : url,
                    'specifications' : specifications,
                    'image_urls' : shoe_urls
                }

            self.driver.close()

        except Exception as e:
            print(e)

        finally:
            self.driver.quit()
        
class MyntraSpider(scrapy.Spider):
    name = 'shoes'
    start_urls = [
        'https://www.myntra.com/casual-shoes/adidas-originals/adidas-originals-men-black-campus-sneakers/1945223/buy',
        'https://www.myntra.com/casual-shoes/nike/nike-men-white-solid-court-royale-sneakers/1800829/buy',
        ]

    def __init__(self):
         self.driver = webdriver.Firefox(options=options)
    
    def parse(self, response):
        self.driver.get(response.url)
        self.driver.execute_script("window.scrollTo(0, 1600)")        
        self.driver.find_element_by_xpath("//div[@class = 'index-showMoreText']").click()
        
        mount_root = Selector(text = self.driver.page_source)
        print(mount_root.re(r'url\("([^\")]+)'))
        row_keys = mount_root.xpath("//*[@class = 'index-rowKey']/text()").getall()
        row_values = mount_root.xpath("//*[@class = 'index-rowValue']/text()").getall()
        specifications = dict(zip(row_keys, row_values))

    def __del__(self):
        self.driver.close()