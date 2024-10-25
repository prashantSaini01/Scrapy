import csv
import re
from playwright.sync_api import sync_playwright

def scrape_linkedin(query, num_posts=10, output_file="linkedin_posts.csv"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})

        # Log in to LinkedIn
        page.goto('https://www.linkedin.com/login')
        page.fill('#username', '2000331530035@rkgit.edu.in')  # Replace with your credentials
        page.fill('#password', 'Roy@1234')
        page.click('button[type="submit"]')

        # Wait for login to complete
        page.wait_for_timeout(5000)

        # Perform search
        search_url = f'https://www.linkedin.com/search/results/content/?keywords={query}'
        page.goto(search_url)

        posts_data = []

        while len(posts_data) < num_posts:
            # Wait for posts to load
            page.wait_for_timeout(3000)

            # Extract posts on the page
            posts = page.query_selector_all('div.update-components-text.relative')

            for post in posts:
                if len(posts_data) >= num_posts:
                    break  # Stop if we've collected enough posts

                # Extract content
                content = post.inner_text().strip()

                # Extract and filter hashtags
                hashtags = extract_unique_hashtags(content)

                # Remove hashtags and the word 'hashtag' from content
                filtered_content = re.sub(r'#\w+', '', content)  # Remove hashtags
                filtered_content = filtered_content.replace('hashtag', '').strip()  # Remove 'hashtag' word

                # Extract author name
                author = post.query_selector('span.feed-shared-actor__name') or post.query_selector('.update-components-actor__name')
                author_name = author.inner_text().strip() if author else "Unknown Author"

                # Extract image URL
                image = post.query_selector('img')
                image_url = image.get_attribute('src') if image else "No Image Available"

                # Extract post URL
                post_url_element = post.query_selector('a.app-aware-link')
                post_url = post_url_element.get_attribute('href') if post_url_element else "No URL"

                # Add the extracted data to the list
                posts_data.append({
                    'Content': filtered_content,
                    'Hashtags': ', '.join(hashtags),
                    #'Image URL': image_url,
                    #'Author': author_name,
                    'Post URL': post_url
                })

            # Scroll down to load more posts if necessary
            if len(posts_data) < num_posts:
                page.mouse.wheel(0, 3000)  # Scroll down

        browser.close()

        # Save data to CSV file
        save_to_csv(posts_data, output_file)

def extract_unique_hashtags(content):
    """Extract unique hashtags from the content."""
    hashtags = re.findall(r'#\w+', content)  # Find all hashtags
    return list(set(hashtags))  # Remove duplicates

def save_to_csv(data, filename):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Content', 'Hashtags', 'Image URL', 'Author', 'Post URL'])
            writer.writeheader()  # Write the header row
            writer.writerows(data)  # Write the post data rows
        print(f"Data successfully saved to '{filename}'.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Run the scraper
scrape_linkedin("machine Learning", num_posts=5, output_file="link2.csv")
