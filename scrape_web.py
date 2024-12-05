import requests
from bs4 import BeautifulSoup
import json
import os
import re
import concurrent.futures

RELEVANT_KEYWORDS = [
    "climate change", "global warming", "carbon emissions", "greenhouse gases",
    "carbon footprint", "Paris Agreement", "climate action", "renewable energy",
    "carbon neutrality", "sustainability", "climate crisis", "greenhouse effect",
    "climate policy", "clean energy", "environmental impact", "extreme weather",
    "carbon taxes", "climate adaptation", "climate mitigation", "fossil fuel",
    "clean technology", "green tech", "electric vehicles", "solar power", "wind power",
    "energy transition", "carbon pricing", "climate finance",
    "carbon credits", "carbon trading", "sustainable development", "climate justice",
    "climate activism", "climate legislation", "climate models",
    "climate science" "oceans and climate change",
    "melting ice", "sea level rise", "biodiversity loss",
    "geoengineering", "natural disasters", "heatwave", "wildfires", "drought", "flooding",
    "hurricane", "sustainable agriculture", "water scarcity",
    "deforestation", "forest conservation",
    "UN climate summit", "COP27", "climate pact", "Net Zero", "Fridays for Future",
    "warming climate", "global temperatures", "changing temperatures", "Warmer temperatures",
    "climate denial"
]


element_removals = {
    "NPR": ["div#story-meta", "div#primaryaudio", "b.credit", "p.hide-caption", "b.toggle-caption"],
    "Phys.Org": ["div.article__info", "p.article-byline", "div.article-main__more", "p.article-main__note", "div.article__info-fc", "div.d-none"],
    "CBS News": ["div.content__meta-wrapper", "div.content-author", "footer.content__footer"],
    "CleanTechnica": ["div.afterpost"],
    "International Business Times": ["div.source"],
    "The Conversation Africa": ["div.content-sidebar"],
    "The Punch": ["div.share-article"],
    "Project Syndicate": ["div.listing", "div.inlay", "section.article__sidebar", "div.end-of-article"],
    "Scientific American": ["p.article_authors-s5nSV", "div.breakoutContainer-8fsaw", "div.newsletterSignup-lj6hJ"],
    "Vox": ["div._135mano3"],
    # "Forbes": ["div.openWeb-wrapper"],
    # "Grist": ["div.membership-ad"],
}

# Source: [tag, class?, id?]
non_article_sites = {
    "Al Jazeera English": ["main"],
    "CBC News": ["div", "detailMainCol"],
    "The Punch": ["div", "post-content"],
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

        # Remove all <footer> tags within the article
        for footer in article_tag.find_all('footer'):
            footer.decompose() 

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


def article_already_saved(url, output_directory):
    """Check if an article has already been saved based on its expected file path"""
    source_name = sanitize_filename(url['source'])
    time = url['time']
    
    # Extract date in 'YYYY-MM-DD' format from the time string
    date = time.split("T")[0]

    # Construct the expected file path
    date_folder = os.path.join(output_directory, date)
    file_name = f"{source_name}_{time.replace(':', '-')}.txt"
    file_path = os.path.join(date_folder, file_name)

    return os.path.exists(file_path)


def scrape_article_content_with_timeout(url, timeout=5):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(scrape_article_content, url)
        try:
            # Try to get the result within the specified timeout
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print(f"Scraping {url['url']} took too long, skipping...")
            return None
        

def is_climate_change_article(article, min_keywords = 3):
    # Count how many relevant keywords are mentioned in the article
    keyword_count = sum(1 for keyword in RELEVANT_KEYWORDS if keyword.lower() in article.lower())

    # Check if at least the required number of keywords appear
    return keyword_count >= min_keywords


def scrape_articles(directory, output_directory):
    urls = load_urls_from_json(directory)
    os.makedirs(output_directory, exist_ok=True)
    
    # Loop through the URLs and scrape each article
    for url in urls:
        if article_already_saved(url, output_directory):
            print(f"Skipping already saved article: {url['url']}")
            continue

        if url["source"] == "Wattsupwiththat.com" or url["source"] == "MIT Technology Review":
            continue

        print(f"Scraping {url['url']}...")
        content = scrape_article_content_with_timeout(url, timeout=5)

        if content:
            if is_climate_change_article(content):
                save_article_content(url, content, output_directory)
                print(f"Saved content")
            else:
                print("Article is not relevant to climate change")
        else:
            print(f"Failed to scrape content from {url}")

        print()

#Input and output directories
json_directory = './to_scrape' 
output_directory = './scraped_articles'

# Run the scraper
scrape_articles(json_directory, output_directory)
