import json
import os
from collections import defaultdict

def count_article_sources(directory):
    source_counts = defaultdict(int)

    # Loop through all JSON files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        # Open and read each JSON file
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            
            # Check if the articles exist in the JSON structure
            if 'articles' in data:
                articles = data['articles']
                
                # Loop through each article and count the source name
                for article in articles:
                    source_name = article['source']['name']
                    source_counts[source_name] += 1

    sorted_sources = dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True))

    # Save the counts to a JSON file
    with open('data/current_article_count.json', 'w', encoding='utf-8') as count_file:
        json.dump(sorted_sources, count_file, indent=4)

    print("Source counts saved to data/current_article_count.json")

# Example usage
count_article_sources('./articles')  # Replace with your actual directory path

