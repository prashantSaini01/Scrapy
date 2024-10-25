from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def login_to_instagram(driver, email, password):
    driver.get('https://www.instagram.com/accounts/login/')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(email)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password'))).send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    WebDriverWait(driver, 10).until(EC.url_changes('https://www.instagram.com/accounts/login/'))

def scrape_images(driver):
    image_urls = []
    
    # Wait for the images to load
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '_aagv')))
    
    # Extract images
    images = driver.find_elements(By.CSS_SELECTOR, 'article img')  # Updated selector for images
    image_urls = [img.get_attribute('src') for img in images]  # Extract the 'src' attribute of each image

    return image_urls

def scrape_instagram(email, password, hashtag):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920x1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        login_to_instagram(driver, email, password)
        driver.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        
        # Scrape images from the hashtag page
        image_urls = scrape_images(driver)
        return image_urls
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    email = "ig_scrapper008"
    password = "happyholi"
    hashtag = "ai"
    
    data = scrape_instagram(email, password, hashtag)
    print(data)
