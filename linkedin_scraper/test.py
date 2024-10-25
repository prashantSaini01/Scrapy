from playwright.sync_api import sync_playwright

def scrape_linkedin(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()

        # Go to LinkedIn login page
        page.goto('https://www.linkedin.com/login')
        page.fill('#username', '2000331530035@rkgit.edu.in')
        page.fill('#password', 'Roy@1234')
        page.click('button[type="submit"]')

        # Wait for navigation and search
        page.wait_for_timeout(5000)  # Allow some time to log in
        page.goto(f'https://www.linkedin.com/search/results/content/?keywords={query}')
        page.wait_for_timeout(5000)

        # Extract post content
        posts = page.query_selector_all('div.update-components-text.relative')
        results = [post.inner_text() for post in posts]

        browser.close()
        return results

# Run the scraping function
print(scrape_linkedin("ai"))
