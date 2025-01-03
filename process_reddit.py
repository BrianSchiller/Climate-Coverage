import json
import string
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from scrape_web import scrape_article_content_with_timeout
from settings import label_keywords
from plots import plot_reddit_keyword_count

def process_reddit_submissions(file):
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



    with open(file) as r:
        submissions = json.load(r)
        
    original_length = len(submissions)
    filtered_submissions = []
    for index, submission in enumerate(submissions):
        print(f"{index}/{original_length}")
        content = submission["Content"]
        if not submission["Selfpost"]:
            article = scrape_article_content_with_timeout({"source": None, "url": submission["URL"]})
            if article is None or article == "":
                print("Failed")
                continue
            else:
                content += article
        content = preprocess_text(content)
        submission["Processed_Content"] = content

        for comment in submission["Comments"]:
            comment["Processed_Content"] = preprocess_text(comment["Content"])

        filtered_submissions.append(submission)

    file_dir, file_name = os.path.split(file)
    file_name_without_ext, ext = os.path.splitext(file_name)
    new_file_name = file_name_without_ext + "_processed" + ext
    new_file_path = os.path.join(file_dir, new_file_name)
    with open(new_file_path, "w") as outfile: 
        json.dump(filtered_submissions, outfile, indent=4)

    print("Finished the processing of reddit submissions. Can be found here: ", new_file_path)
    return new_file_path


def count_keywords(file):
    with open(file) as r:
        submissions = json.load(r)

    for submission in submissions:
        submission["labels"] = {}
        submission["comment_labels"] = {}

        for category, labels in label_keywords.items():
            for label, keywords in labels.items():
                if label not in submission["labels"].keys():
                    submission["labels"][label] = 0

                for keyword in keywords:
                    count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', submission["Processed_Content"]))
                    submission["labels"][label] += count

        for category, labels in label_keywords.items():
            for label, keywords in labels.items():
                if label not in submission["comment_labels"].keys():
                    submission["comment_labels"][label] = 0
                    
                    for comment in submission["Comments"]:
                        for keyword in keywords:
                            count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', comment["Processed_Content"]))
                            submission["comment_labels"][label] += count

    with open(file, "w") as outfile: 
        json.dump(submissions, outfile, indent=4)

    print(f"Counted keywords in {file}")

    return submissions


def count_topics_per_subreddit(subreddits):
    scores = {}

    for subreddit in subreddits:
        scores[subreddit] = {"scores": {}, "comment_scores": {}}
        for category, labels in label_keywords.items():
            for label, keywords in labels.items():
                scores[subreddit]["scores"][label] = 0
                scores[subreddit]["comment_scores"][label] = 0

        file_path = f"reddit/{subreddit}_processed.json"
        with open(file_path) as r:
            submissions = json.load(r)

        scores[subreddit]["num_of_sub"] = len(submissions)
        for submission in submissions:
            for label, value in submission["labels"].items():
                scores[subreddit]["scores"][label] += value
            for label, value in submission["comment_labels"].items():
                scores[subreddit]["comment_scores"][label] += value
    
    file = "reddit/subreddit_topics.json"
    with open(file, "w") as outfile: 
        json.dump(scores, outfile, indent=4)

    print(f"Counted keywords in {file}")

# subreddit = "climateskeptics"
# output = process_reddit_submissions(f'reddit/{subreddit}.json')
# submissions = count_keywords(output)
# plot_reddit_keyword_count(submissions, subreddit)

subreddits = ["climate", "climatechange", "climateskeptics"]
count_topics_per_subreddit(subreddits)