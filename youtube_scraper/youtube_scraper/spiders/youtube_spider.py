import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class YoutubeSpider(scrapy.Spider):
    name = "youtube"

    def __init__(self, search_query="fitness", *args, **kwargs):
        super(YoutubeSpider, self).__init__(*args, **kwargs)
        self.search_query = search_query

        # Set up Selenium with Chrome in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def start_requests(self):
        url = f"https://www.youtube.com/results?search_query={self.search_query}"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(5)  # Wait for the page to load

        videos = self.driver.find_elements(By.XPATH, '//a[@id="video-title"]')

        for video in videos[:10]:  # Scrape only the top 10 results
            yield {
                "title": video.get_attribute("title"),
                "url": video.get_attribute("href")
            }

        self.driver.quit()

# In your Scrapy settings.py, ensure you have the following:
# FEED_FORMAT = 'json'
# FEED_URI = 'output.json'
