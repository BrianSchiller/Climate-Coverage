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
        domains="""phys.org, theconversation.com,
                    cbc.ca, cbsnews.com,
                    project-syndicate.org, bbc.com, sciencedaily.com,
                    ibtimes.com, npr.org, time.com, 
                    businessinsider.com, scientificamerican.com,
                    cleantechnica.com, vox.com, globalsecurity.org,
                    punchng.com, aljazeera.com"""
    )
    
    with open(file_name, 'w') as json_file:
        json.dump(top_headlines, json_file, indent=4)

    print(f"Data successfully written to articles_{date_str}.json")

# Set the start and end dates
end_date = datetime(2024, 12, 30)
start_date = end_date - timedelta(days=30)

directory = "articles"
clean_directory = "clean_articles"
os.makedirs(directory, exist_ok=True)

# Loop through each day
for i in range(31):
    current_date = start_date + timedelta(days=i)
    fetch_articles(current_date)

print("Data fetching completed for the last 30 days.")

count_article_sources(directory)

