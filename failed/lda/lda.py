from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from preprocess_articles import preprocess_articles
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

label_keywords = {
    "causes": {
        "Energy and Industry": [
            "Fossil Fuels", "Energy", "Industry", "Transportation", 
            "Emissions", "Oil", "Gas", "Coal", "Pollution", 
            "Electricity", "Power Plants"
        ],
        "Land Use and Agriculture": [
            "Deforestation", "Agriculture", "Farming", "Land Use", 
            "Soil Degradation", "Crops", "Land Clearing", "Land Management"
        ],
        "Governance and Policy Failures": [
            "Policy", "Governance", "Government", 
            "Inaction", "Policy Gaps", "Legislation"
        ],
        "Personal Consumption": [
            "Consumption", "Overconsumption", "Waste", 
            "Footprint", "Lifestyle", "Carbon Footprint", "Resource Use"
        ]
    },
    "consequences": {
        "Ecosystem Disruption": [
            "Biodiversity", "Ecosystem", "Habitat Loss", "Coral Bleaching", 
            "Species Extinction", "Deforestation", "Wetlands", 
            "Marine Life", "Forest Degradation", "Ecosystem Collapse", 
            "Soil Erosion", "Invasive Species"
        ],
        "Extreme Weather Events": [
            "Heatwaves", "Flooding", "Drought", "Wildfires", "Hurricanes", 
            "Tornadoes", "Storms", "Cyclones", "Typhoons", "Extreme Temperatures", 
            "Floods", "Weather Patterns", "Disaster", "Climate Events"
        ],
        "Health Risks": [
            "Health", "Diseases", "Air Pollution", "Water Pollution", "Heat Stroke", 
            "Malnutrition", "Vector-Borne Diseases", "Respiratory Illness", "Heart Disease", 
            "Cancer", "Water Scarcity", "Mental Health", "Vulnerable Populations", 
            "Nutrition", "Infectious Disease", "Illness"
        ],
        "Economic Impact": [
            "Economic Impact", "Cost", "Losses", "Food Security", 
            "Infrastructure Damage", "Economic Growth", "Insurance", "Investment", 
            "GDP", "Job Loss", "Poverty",
        ],
        "Displacement and Migration": [
            "Migration", "Displacement", "Climate Refugees",
            "Sea Level Rise", "Natural Disasters", "Conflict",
            "Loss of Livelihood", "Environmental Refugees", "Relocation"
        ]
    },
    "solutions": {
        "Technological Solutions": [
            "Renewable Energy", "Solar", "Wind", "Electric Vehicles", 
            "Efficiency", "Green Tech", "Storage", "Hydrogen"
        ],
        "Governance and Policy": [
            "Policy", "Climate Action", "Agreements", "Net Zero", 
            "Carbon Pricing", "Regulation"
        ],
        "Adaptation and Resilience": [
            "Adaptation", "Resilience", "Infrastructure", 
            "Disaster Management", "Urban Planning", "Water Management"
        ],
        "Nature-Based Solutions": [
            "Reforestation", "Ecosystems", "Conservation", "Wetlands", 
            "Forests", "Coastal Protection", "Sustainability"
        ]
    }
}

# Number of topics for LDA
n_topics = 10  # Modify as needed

def get_synthetic_sentences_with_labels():
    with open('data/synthetic_sentences.json', 'r') as f:
        synthetic_sentences = json.load(f)

    sentences = []
    labels = []

    for label, sentences_list in synthetic_sentences.items():
        for sentence in sentences_list:
            sentences.append(sentence)
            labels.append(label)

    return sentences, labels

# Preprocess original articles & Prepare synthetic data
article_df, _ = preprocess_articles()
synthetic_sentences_, synthetic_labels = get_synthetic_sentences_with_labels()

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

synthetic_sentences = [preprocess_text(t) for t in synthetic_sentences_]

# Combine original articles and synthetic sentences
all_texts = list(article_df['Text']) + synthetic_sentences
all_labels = ["Original"] * len(article_df) + synthetic_labels

# Use CountVectorizer for LDA
count_vectorizer = CountVectorizer(max_features=5000, ngram_range=(1, 2), stop_words='english')
X_counts = count_vectorizer.fit_transform(all_texts)

# Fit LDA model
lda = LatentDirichletAllocation(n_components=n_topics, random_state=42, learning_method='batch')
lda.fit(X_counts)

# Get topics and their corresponding words
feature_names = count_vectorizer.get_feature_names_out()
word_distributions = []

def get_topic_words():
    topic_words = {}
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[-10:]]
        topic_words[f"Topic_{topic_idx}"] = top_words
    return topic_words

# Map each text to its most probable topic
text_topic_distribution = lda.transform(X_counts)

# Separate original articles' topic distributions
original_articles_topics = text_topic_distribution[:len(article_df)]
synthetic_topics = text_topic_distribution[len(article_df):]

# Store topic probabilities for each text
text_topics = []
for i, distribution in enumerate(text_topic_distribution):
    best_topic = distribution.argmax()
    text_topics.append((all_texts[i], all_labels[i], best_topic, distribution[best_topic]))

# Aggregate topics for each label
def aggregate_topics_by_label(text_topics):
    label_topic_map = {}

    for text, label, topic, probability in text_topics:
        if label not in label_topic_map:
            label_topic_map[label] = []
        label_topic_map[label].append(topic)

    label_to_topics = {}
    for label, topics in label_topic_map.items():
        # Count the most common topics and select the top 1-2
        topic_counts = pd.Series(topics).value_counts()
        label_to_topics[label] = topic_counts.index[:2].tolist()

    return label_to_topics

# Process the topics for each label
label_to_topics = aggregate_topics_by_label(text_topics)

# Save results
topic_words = get_topic_words()
with open('label_to_topics.json', 'w') as f:
    json.dump(label_to_topics, f, indent=4)

with open('topic_words.json', 'w') as f:
    json.dump(topic_words, f, indent=4)

# Save individual original articles' topic distributions
original_articles_df = article_df.copy()
original_articles_df[[f"Topic_{i}" for i in range(n_topics)]] = original_articles_topics
original_articles_df.to_csv("data/original_articles_topics.csv", index=False)

print("Processed labels to topics mapping and saved to JSON.")
print(f"Original articles' topic distributions saved to 'data/original_articles_topics.csv'.")