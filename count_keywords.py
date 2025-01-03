import os
import string
import json
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from settings import label_keywords
import plots

def load_articles(folder_path):
    results = {}

    # Initialize nltk resources
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    # Initialize preprocessing tools
    stop_words = set(stopwords.words('english'))
    stop_words.update(["-", "’", "“", "”", "‘", "’", "—", "–", "climate", "change"])
    lemmatizer = WordNetLemmatizer()

    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = word_tokenize(text)
        words = [word for word in words if word not in stop_words]
        words = [lemmatizer.lemmatize(word) for word in words]
        return ' '.join(words)

    # Traverse through all files in the folder and subfolders
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                # Extract newspaper name from filename
                newspaper_name = file.split('_')[0]
                timestamp = file.split('_')[1]
                
                # Read the article content
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = preprocess_text(f.read())

                if newspaper_name not in results.keys():
                    results[newspaper_name] = {}

                results[newspaper_name][timestamp] = content

                # print(f"Processed content for {file}: {content}")
    # print(results["Phys.Org"])
    return results

def count_keywords(articles):
    counter = {}

    for newspaper, dates in articles.items():
        counter[newspaper] = {"labels": {}, "num_articles": len(dates)}
        for date, content in dates.items():

            for category, labels in label_keywords.items():
                for label, keywords in labels.items():
                    print(counter[newspaper]["labels"].keys())
                    if label not in counter[newspaper]["labels"].keys():
                        counter[newspaper]["labels"][label] = 0
                    print(counter[newspaper]["labels"])

                    for keyword in keywords:
                        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content))
                        counter[newspaper]["labels"][label] += count

    return counter

# Specify the folder path containing the articles
folder_path = "scraped_articles" 
articles = load_articles(folder_path)
counter = count_keywords(articles)
plots.plot_article_keyword_count(counter)
with open("data/article_keyword_count.json", "w") as outfile: 
    json.dump(counter, outfile)

# Print the results
# print_results(results)