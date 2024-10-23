import json
import os
from newsapi import NewsApiClient
from datetime import datetime, timedelta

from count import count_article_sources

# Initialize News API Client
newsapi = NewsApiClient(api_key='0bafdd1fa77c4b78b485c2236dddb614')

# Function to fetch and save articles for a given date
def fetch_articles(date):
    date_str = date.strftime('%Y-%m-%d')
    to_time = date.strftime('%Y-%m-%dT23:59:59')

    file_name = f'{directory}/articles_{date_str}.json'

    if os.path.exists(file_name):
        print(f"File {file_name} already exists. Skipping API call.")
        return

    # Fetch articles for that specific day
    top_headlines = newsapi.get_everything(
        q='climate change',
        language='en',
        page_size=100,
        sort_by="relevancy",
        from_param=date_str,
        to=to_time,
        exclude_domains="""bringatrailer.com, removed.com, abcnews, abcnews.go, 
                        subscriber.politicopro.com, biztoc.com, japantoday.com,
                        www.cbsnews.com/video, qz.com, skepticalscience.com,
                        www.autocar.co.uk, thehindubusinessline.com"""
    )
    
    with open(file_name, 'w') as json_file:
        json.dump(top_headlines, json_file, indent=4)

    print(f"Data successfully written to articles_{date_str}.json")


def clean_data():
    # valid_sources = sources that appear at least 3 times
    with open('data/current_article_count.json', 'r', encoding='utf-8') as count_file:
        source_counts = json.load(count_file)
    valid_sources = {source for source, count in source_counts.items() if count >= 3}

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            
            filtered_articles = [article for article in data['articles'] 
                                    if article['source']['name'] not in remove_domains
                                        and article['source']['name'] in valid_sources]

            # Create a new dictionary to store the filtered results
            filtered_data = {
                "status": data['status'],
                "totalResults": data['totalResults'],
                "fetchedResults": len(data['articles']),
                "cleanedResults": len(filtered_articles),
                "articles": filtered_articles
            }

            clean_file_path = os.path.join(clean_directory, filename)
            # Save the filtered data to a new JSON file
            with open(clean_file_path, 'w', encoding='utf-8') as file:
                json.dump(filtered_data, file, indent=4)

# Set the start and end dates
end_date = datetime(2024, 10, 23)
start_date = end_date - timedelta(days=30)

directory = "articles"
clean_directory = "clean_articles"
os.makedirs(directory, exist_ok=True)

# Loop through each day
for i in range(30):
    current_date = start_date + timedelta(days=i)
    fetch_articles(current_date)

print("Data fetching completed for the last 30 days.")


response = input("Clean data?")

if response == "y":
    os.makedirs(clean_directory, exist_ok=True)
    count_article_sources(directory)
    remove_domains = ["[Removed]", "ABC News"]
    clean_data()
    print("Finished Data Cleaning")

