import csv
import re
import streamlit as st
import asyncio
from playwright.async_api import async_playwright

async def scrape_linkedin(query, num_posts=10):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set to True for headless mode
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1280, "height": 720})

        # Log in to LinkedIn
        await page.goto('https://www.linkedin.com/login')
        await page.fill('#username', st.session_state.username)  # Use Streamlit session state for credentials
        await page.fill('#password', st.session_state.password)
        await page.click('button[type="submit"]')

        # Wait for login to complete
        await page.wait_for_timeout(5000)

        # Perform search
        search_url = f'https://www.linkedin.com/search/results/content/?keywords={query}'
        await page.goto(search_url)

        posts_data = []

        while len(posts_data) < num_posts:
            # Wait for posts to load
            await page.wait_for_timeout(3000)

            # Extract posts on the page
            posts = await page.query_selector_all('div.update-components-text.relative')

            for post in posts:
                if len(posts_data) >= num_posts:
                    break  # Stop if we've collected enough posts

                # Extract content
                content = await post.inner_text()
                content = content.strip()

                # Extract and filter hashtags
                hashtags = extract_unique_hashtags(content)

                # Remove hashtags and the word 'hashtag' from content
                filtered_content = re.sub(r'#\w+', '', content)  # Remove hashtags
                filtered_content = filtered_content.replace('hashtag', '').strip()  # Remove 'hashtag' word

                # Extract author name
                author = await post.query_selector('span.feed-shared-actor__name') or await post.query_selector('.update-components-actor__name')
                author_name = await author.inner_text() if author else "Unknown Author"

                # Extract image URL
                image = await post.query_selector('img')
                image_url = await image.get_attribute('src') if image else "No Image Available"

                # Extract post URL
                post_url_element = await post.query_selector('a.app-aware-link')
                post_url = await post_url_element.get_attribute('href') if post_url_element else "No URL"

                # Add the extracted data to the list
                posts_data.append({
                    'Content': filtered_content,
                    'Hashtags': ', '.join(hashtags),
                    'Image URL': image_url,
                    'Author': author_name,
                    'Post URL': post_url
                })

            # Scroll down to load more posts if necessary
            if len(posts_data) < num_posts:
                await page.mouse.wheel(0, 3000)  # Scroll down

        await browser.close()
        return posts_data

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
        return filename
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

# Streamlit UI
st.title("LinkedIn Scraper")

# Input for LinkedIn Credentials
st.subheader("LinkedIn Credentials")
username = st.text_input("Username/Email", "")
password = st.text_input("Password", type="password", value="")

# Input for Search Query and Number of Posts
st.subheader("Scraping Options")
query = st.text_input("Search Query", "machine Learning")
num_posts = st.number_input("Number of Posts to Scrape", min_value=1, max_value=100, value=5)

if st.button("Scrape"):
    if username and password:
        st.session_state.username = username
        st.session_state.password = password

        # Call the scraping function
        posts_data = asyncio.run(scrape_linkedin(query, num_posts))
        st.success("Scraping completed!")

        # Display the results
        if posts_data:
            st.write(f"Extracted {len(posts_data)} posts:")
            for post in posts_data:
                st.write(f"**Author:** {post['Author']}")
                st.write(f"**Content:** {post['Content']}")
                st.write(f"**Hashtags:** {post['Hashtags']}")
                st.write(f"[Post URL]({post['Post URL']})")
                st.image(post['Image URL'])
                st.markdown("---")

            # Save to CSV
            filename = save_to_csv(posts_data, "linkedin_posts.csv")
            if filename:
                st.success(f"Data successfully saved to '{filename}'.")
        else:
            st.warning("No posts found.")
    else:
        st.error("Please enter your LinkedIn credentials.")
