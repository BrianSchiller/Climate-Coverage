import requests
from bs4 import BeautifulSoup
import json
import os
import re
import concurrent.futures

element_removals = {
    "NPR": ["div#story-meta", "div#primaryaudio", "b.credit", "p.hide-caption", "b.toggle-caption"],
    "Phys.Org": ["div.article__info", "p.article-byline", "div.article-main__more", "p.article-main__note", "div.article__info-fc", "div.d-none"],
    "Forbes": ["div.openWeb-wrapper"],
    "Grist": ["div.membership-ad"]
}

# Source: [tag, class?, id?]
non_article_sites = {
    "Al Jazeera English": ["main"],
    "Wattsupwiththat.com": ["div", "entry-content"],
    "CBC News": ["div", "detailMainCol"],
    "CounterPunch": ["div", "post_content"],
    "Hurriyet Daily News": ["div", "content"],
    "VOA News": ["div", "", "article-content"],
    "Investing.com": ["div", "article_container"],
    "Globalsecurity.org": ["div", "", "content"],
    "Newsweek": ["div", "article-body"],
    "TheJournal.ie": ["div", "article-body-redesign"],
    "Slashdot.org": ["div", "body"],
    "MIT Technology Review": ["div", "", "content--body"],
    "gcaptain.com": ["div", "body"],
    "PBS": ["article", "articleBody"],
    "Science Daily": ["div", "", "story_text"],
    # "Forbes": ["div", "body-container"],
    "Energycentral.com": ["div", "field "]
}

def load_urls_from_json(directory):
    urls = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                if 'articles' in data:
                    for article in data['articles']:
                        urls.append(
                            {"source": article["source"]["name"],
                            "time": article["publishedAt"],
                            "url": article['url']}
                        )
    
    return urls


def scrape_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        # Fetch the web page
        response = requests.get(url["url"], headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find the relevant content
        if not url["source"] in non_article_sites:
            # Use <article>
            article_tag = soup.find('article')
        else:
            # Check if there is an alternative to <article>
            alt_tag = non_article_sites[url["source"]]

            if len(alt_tag) == 1:
                # Just look for a element (e.g. main)
                article_tag = soup.find(alt_tag[0])
            elif len(alt_tag) == 2:
                # Look for an element with a class name
                article_tag = soup.find(alt_tag[0], class_=alt_tag[1])
            else:
                # Look for an element with an id
                article_tag = soup.find(alt_tag[0], id=alt_tag[2])

        # If no relevant content, return None
        if article_tag is None:
            print(f"No <article> tag found for {url}")
            return None
        
        # Remove elements based on the source configuration
        if url["source"] in element_removals:
            for selector in element_removals[url["source"]]:
                for element in article_tag.select(selector):
                    element.decompose()  # Remove the element and its contents
        
        # Remove all <aside> tags within the article
        for aside in article_tag.find_all('aside'):
            aside.decompose() 

        # Remove all <button> tags within the article
        for button in article_tag.find_all('button'):
            button.decompose()
        

        article = []
        for p in article_tag.find_all('p'):
            # Get text while preserving <a> tags within the same line
            p_text = p.get_text(separator=' ', strip=True)  # Use space as separator for in-line text
            article.append(p_text)

        return '\n'.join(article)

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def save_article_content(url, content, output_directory):
    source_name = sanitize_filename(url['source'])
    time = url['time']
    
    # Extract date in 'YYYY-MM-DD' format from the time string
    date = time.split("T")[0]

    # Create a subfolder for the date
    date_folder = os.path.join(output_directory, date)
    os.makedirs(date_folder, exist_ok=True)

    # Construct the file name using the sanitized source and time
    file_name = f"{source_name}_{time.replace(':', '-')}.txt"
    file_path = os.path.join(date_folder, file_name)

    # Save the content to a file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def scrape_article_content_with_timeout(url, timeout=5):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(scrape_article_content, url)
        try:
            # Try to get the result within the specified timeout
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Scraping {url['url']} took too long, skipping...")
            return None


def scrape_articles(directory, output_directory):
    urls = load_urls_from_json(directory)
    os.makedirs(output_directory, exist_ok=True)
    
    # Loop through the URLs and scrape each article
    for url in urls:
        print(f"Scraping {url['url']}...")
        content = scrape_article_content_with_timeout(url, timeout=5)

        if content:
            save_article_content(url, content, output_directory)
            print(f"Saved content from {url['url']}")
        else:
            print(f"Failed to scrape content from {url}")

        print()

#Input and output directories
json_directory = './to_scrape' 
output_directory = './scraped_articles'

# Run the scraper
scrape_articles(json_directory, output_directory)
