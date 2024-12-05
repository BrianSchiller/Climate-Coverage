import os
import json
import pandas as pd
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
from sklearn.preprocessing import MultiLabelBinarizer


def preprocess_articles(articles_path = 'scraped_articles' , data_label_path = 'data/article_labels.json'):
    # Step 2: Define the function to find articles in subfolders
    def find_article_texts(base_folder, keys):
        articles_found = []
        
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                # Check if the file name corresponds to any key in the articles_data
                for key in keys:
                    key_txt = key + ".txt"
                    if key_txt in file:
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as article_file:
                            text = article_file.read()
                        articles_found.append((key, text))
                        keys.remove(key)
                        break
                    
        return articles_found

    # Load the JSON data
    with open(data_label_path, 'r') as file:
        data = json.load(file)

    # Create DataFrame
    articles_data = data.get("articles", {})
    article_texts = find_article_texts(articles_path, list(articles_data.keys()))

    # Prepare data for DataFrame
    data_for_df = []
    for article_key, article_text in article_texts:
        # Split key into source and timestamp
        source, timestamp = article_key.split('_', 1)
        labels = articles_data[article_key]
        data_for_df.append((source, labels, article_text))

    df = pd.DataFrame(data_for_df, columns=['Source', 'Labels', 'Text'])

    # Display the DataFrame
    print(df)


    # Initialize nltk resources
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    # Initialize preprocessing tools
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    def preprocess_text(text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = word_tokenize(text)
        words = [word for word in words if word not in stop_words]
        words = [lemmatizer.lemmatize(word) for word in words]
        return ' '.join(words)

    # Preprocess the text
    df['Text'] = df['Text'].apply(preprocess_text)

    df.to_json("data/processed_articles.json", orient='records', lines=True)


    # Initialize MultiLabelBinarizer
    mlb = MultiLabelBinarizer()

    # Transform labels into binary format
    Y = mlb.fit_transform(df['Labels'])

    # Create a DataFrame for the binary labels
    labels_df = pd.DataFrame(Y, columns=mlb.classes_)

    return df, labels_df