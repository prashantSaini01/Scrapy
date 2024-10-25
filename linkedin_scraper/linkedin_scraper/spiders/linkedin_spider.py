import scrapy
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class LinkedInSpider(scrapy.Spider):
    name = "linkedin"

    def __init__(self, email, password, query, *args, **kwargs):
        super(LinkedInSpider, self).__init__(*args, **kwargs)
        self.email = email
        self.password = password
        self.query = query
        self.driver = None

        # Set up Selenium with Chrome in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # Uncomment to run in headless mode
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def start_requests(self):
        yield scrapy.Request(url='https://www.linkedin.com/login', callback=self.login)

    def login(self, response):
        self.driver.get(response.url)
        time.sleep(2)
        email_input = self.driver.find_element(By.ID, 'username')
        password_input = self.driver.find_element(By.ID, 'password')
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_button.click()
        time.sleep(10)  # Wait for the login to complete

        # After logging in, perform the search for posts
        self.perform_search(self.query)

    def perform_search(self, query):
        # Apply the post filter by using the correct search URL format for posts
        search_url = f'https://www.linkedin.com/search/results/content/?keywords={query}'
        
        self.driver.get(search_url)
        time.sleep(5)  # Allow time for the page to load
        
        self.scroll_and_extract()

    def scroll_and_extract(self, max_scroll=2):
        """Scroll through the search results and extract post data."""
        all_urls_and_content = []
        for _ in range(max_scroll):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Allow time for content to load
            urls_and_content = self.extract_urls_and_content()
            all_urls_and_content.extend(urls_and_content)

        # Save to CSV after extracting all the posts
        self.save_to_csv(all_urls_and_content)
        self.driver.quit()

    def extract_urls_and_content(self):
        """Extract URLs and post content from the search results."""
        urls_and_content = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Find all post containers
        containers = soup.find_all('div', {'class': 'update-components-text relative update-components-update-v2__commentary'})
        
        for container in containers:
            spans = container.find_all('span', {'dir': 'ltr'})
            post_content = ' '.join(span.get_text(separator=' ', strip=True) for span in spans)
            link_tag = container.find_parent('a', {'class': 'app-aware-link'})
            url = link_tag['href'] if link_tag and 'href' in link_tag.attrs else 'N/A'
            urls_and_content.append((url, post_content))

        return urls_and_content

    def save_to_csv(self, data, filename='linkedin_posts.csv'):
        """Save the extracted data to a CSV file."""
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['URL', 'Post Content'])
            for url, post_content in data:
                writer.writerow([url, post_content])

# Run the spider from the command line with:
# scrapy crawl linkedin -a email="your_email" -a password="your_password" -a query="your_search_query"
