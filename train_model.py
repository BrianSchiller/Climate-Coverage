from scipy.sparse import hstack, vstack
from lightgbm import LGBMClassifier
from preprocess_articles import preprocess_articles
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import json


# Define label-specific keywords
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

def get_synthetic_sentences():
    # Load synthetic sentences from the JSON file
    with open('data/synthetic_sentences.json', 'r') as f:
        synthetic_sentences = json.load(f)

    # Prepare synthetic data
    synthetic_texts = []
    synthetic_targets = []

    for group, _ in label_keywords.items():
        for label, keywords in label_keywords[group].items():
            for keyword in keywords:
                for sentences in synthetic_sentences[keyword]:
                    print(sentences)
                    synthetic_texts.append(sentences)
                    synthetic_targets.append(label)

    # Create synthetic DataFrame
    synthetic_df = pd.DataFrame({'Text': synthetic_texts})

    # Add binary columns for labels based on the keywords used
    for group, _ in label_keywords.items():
        for label, keywords in label_keywords[group].items():
            synthetic_df[label + "_keywords"] = [
                1 if any(keyword.lower() in text.lower() for keyword in keywords) else 0
                for text in synthetic_df['Text']
            ]

    print(synthetic_df)
    
    return synthetic_df, synthetic_targets

# Function to count keyword occurrences
def keyword_features(text, keywords):
    return sum(text.count(keyword) for keyword in keywords)


# Step 1: Prepare synthetic data
synthetic_df, synthetic_targets = get_synthetic_sentences()

mlb = MultiLabelBinarizer()
synthetic_labels_df = pd.DataFrame(
    mlb.fit_transform([[target] for target in synthetic_targets]),
    columns=mlb.classes_
)

# Step 2: Preprocess original articles (real data)
article_df, labels_df = preprocess_articles()

# Step 3: Convert text to TF-IDF features for original dataset
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_tfidf_real = tfidf_vectorizer.fit_transform(article_df['Text'])

# Get the exact same keyword columns for both datasets
keyword_columns = [col for col in article_df.columns if '_keywords' in col]

# Add keyword-based features for the real data
real_keyword_features = article_df[keyword_columns].values

# Combine TF-IDF features with keyword-based features for real data
X_real = hstack([X_tfidf_real, real_keyword_features])

# Step 4: Split real data into train and test sets
X_train_real, X_test_real, y_train_real, y_test_real, train_idx, test_idx = train_test_split(
    X_real, labels_df, article_df.index, test_size=0.4, random_state=12
)

# Step 5: Process synthetic data
X_tfidf_synthetic = tfidf_vectorizer.transform(synthetic_df['Text'])

# Make sure to use the exact same keyword columns
synthetic_keyword_features = synthetic_df[keyword_columns].values
X_synthetic = hstack([X_tfidf_synthetic, synthetic_keyword_features])
X_train_combined = vstack([X_train_real, X_synthetic])

# Make sure synthetic_labels_df has the same columns as y_train_real
synthetic_labels_df = synthetic_labels_df[y_train_real.columns]

# Fill any NaN values with 0
y_train_real = y_train_real.fillna(0)
synthetic_labels_df = synthetic_labels_df.fillna(0)

# Combine the labels
y_train_combined = pd.concat([y_train_real, synthetic_labels_df], ignore_index=True)

# Now fit the model
model = MultiOutputClassifier(LGBMClassifier(n_estimators=200, max_depth=10, class_weight='balanced'))
model.fit(X_train_combined, y_train_combined)

# Step 7: Test the model on the real test set (excluding synthetic data from test)
y_pred = model.predict(X_test_real)

# Step 8: Evaluate the model
print(classification_report(y_test_real, y_pred, target_names=labels_df.columns))


## Get Output
X_test_articles = article_df.loc[test_idx]

# Convert predicted labels to a DataFrame
y_pred_df = pd.DataFrame(y_pred, columns=labels_df.columns, index=test_idx)

# Convert true labels to a DataFrame
y_test_df = pd.DataFrame(y_test_real, columns=labels_df.columns, index=test_idx)

# Combine article text, true labels, and predicted labels
output_df = pd.concat([X_test_articles['Text'],
                    y_test_df.add_prefix('True_'), 
                    y_pred_df.add_prefix('Predicted_')], axis=1)

# Display the results
output_df.to_csv('output.csv', index=False)
print("Output saved to 'output.csv'")