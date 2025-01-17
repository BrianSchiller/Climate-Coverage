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
    print("Finished loading all articles")
    return results

def count_keywords_per_newspaper(articles):
    counter = {}

    for newspaper, dates in articles.items():
        counter[newspaper] = {"labels": {}, "num_articles": len(dates)}
        for date, content in dates.items():

            for category, labels in label_keywords.items():
                for label, keywords in labels.items():
                    if label not in counter[newspaper]["labels"].keys():
                        counter[newspaper]["labels"][label] = 0

                    for keyword in keywords:
                        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content))
                        counter[newspaper]["labels"][label] += count

    path = "data/newspaper_keyword_count.json"
    with open(path, "w") as outfile: 
        json.dump(counter, outfile)

    print(f"Counted keywords and written to: {path}")

    return counter

def count_keywords_per_newspaper(articles, normalized=False):
    counter = {}

    for newspaper, dates in articles.items():
        counter[newspaper] = {"labels": {}, "num_articles": len(dates)}

        for date, content in dates.items():
            article_label_counts = {}  # Store counts for labels in this article
            total_label_count = 0  # Total keyword count for normalization in this article

            # First pass: calculate counts per label for this article
            for category, labels in label_keywords.items():
                for label, keywords in labels.items():
                    if label not in article_label_counts:
                        article_label_counts[label] = 0

                    for keyword in keywords:
                        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content))
                        article_label_counts[label] += count
                        total_label_count += count

            # Second pass: update overall counter, applying normalization if required
            for label, count in article_label_counts.items():
                if label not in counter[newspaper]["labels"]:
                    counter[newspaper]["labels"][label] = 0

                if normalized and total_label_count > 0:
                    counter[newspaper]["labels"][label] += count / total_label_count
                else:
                    counter[newspaper]["labels"][label] += count

    path = "data/newspaper_keyword_count.json"
    if normalized: 
        path = "data/newspaper_keyword_count_normalized.json"
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(counter, outfile, indent=4)
    
    print(f"Counted keywords and written to: {path}")

    return counter


def count_keywords_per_article(articles, normalized = False):
    counter = {}

    for newspaper, dates in articles.items():
        counter[newspaper] = {}
        for date, content in dates.items():
            counter[newspaper][date] = {}
            article_label_counts = {}  # Store counts for labels in this article
            total_label_count = 0  # Total keyword count for normalization in this article

            # First pass: calculate counts per label for this article
            for category, labels in label_keywords.items():
                for label, keywords in labels.items():
                    if label not in article_label_counts:
                        article_label_counts[label] = 0

                    for keyword in keywords:
                        count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', content))
                        article_label_counts[label] += count
                        total_label_count += count
            
            # Second pass: update counter, applying normalization if required
            for label, count in article_label_counts.items():
                if normalized and total_label_count > 0:
                    counter[newspaper][date][label] = count / total_label_count
                else:
                    counter[newspaper][date][label] = count

    path = "data/article_keyword_count.json"
    if normalized:
        path = "data/article_keyword_count_normalized.json"
    with open(path, 'w', encoding='utf-8') as count_file:
        json.dump(counter, count_file, indent=4)
    print(f"Written article keyword counts to: {path}")
    
    return counter

def identify_topics_per_newspaper(counter):
    scores = {}

    for newspaper, timestamps in counter.items():
        # Construct scores dictionary
        scores[newspaper] = {"scores": {}}
        for category, labels in label_keywords.items():
            for label, keywords in labels.items():
                scores[newspaper]["scores"][label] = 0

        for timestamp, topics in timestamps.items():
            max_value = max(topics.values())
            most_referenced = [topic for topic, value in topics.items() if value == max_value]
            scores[newspaper][timestamp] = most_referenced
            # Count overall occurence
            for label in most_referenced:
                scores[newspaper]["scores"][label] += 1

    path = 'data/newspaper_topic_count.json'
    with open(path, 'w', encoding='utf-8') as count_file:
        json.dump(scores, count_file, indent=4)
    print(f"Written article topic scores to: {path}")

    return scores

# Specify the folder path containing the articles
folder_path = "scraped_articles" 
articles = load_articles(folder_path)

counter = count_keywords_per_newspaper(articles)
plots.plot_newspaper_keyword_count(counter)

counter = count_keywords_per_newspaper(articles, normalized=True)
plots.plot_newspaper_keyword_count(counter, normalized=True)

counter = count_keywords_per_article(articles)
scores = identify_topics_per_newspaper(counter)
plots.plot_newspaper_topic_count(scores)

counter = count_keywords_per_article(articles, normalized=True)