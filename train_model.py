from scipy.sparse import hstack
from lightgbm import LGBMClassifier
from preprocess_articles import preprocess_articles
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer


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
            "Policy", "Governance", "Government", "Regulation", 
            "Climate Action", "Inaction", "Policy Gaps", "Legislation"
        ],
        "Personal Consumption": [
            "Consumption", "Overconsumption", "Waste", 
            "Footprint", "Lifestyle", "Carbon Footprint", "Resource Use"
        ]
    },
    "consequences": {
        "Ecosystem Disruption": [
            "Biodiversity", "Ecosystem", "Habitat Loss", "Coral Bleaching", 
            "Species Extinction", "Pollution", "Deforestation", "Wetlands", 
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
            "Economic Impact", "Cost", "Losses", "Agriculture", "Food Security", 
            "Infrastructure Damage", "Economic Growth", "Insurance", "Investment", 
            "GDP", "Job Loss", "Poverty",
        ],
        "Displacement and Migration": [
            "Migration", "Displacement", "Climate Refugees"
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
            "Carbon Pricing", "Sustainability", "Regulation"
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

# Preprocess articles and labels
article_df, labels_df = preprocess_articles()

# Function to count keyword occurrences
def keyword_features(text, keywords):
    return sum(text.count(keyword) for keyword in keywords)

# Add keyword-based features
for label, keywords in label_keywords.items():
    article_df[label + "_keywords"] = article_df['Text'].apply(lambda x: keyword_features(x.lower(), keywords))

# Convert cleaned text to TF-IDF features
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_tfidf = tfidf_vectorizer.fit_transform(article_df['Text'])

# Combine TF-IDF and keyword-based features
X_combined = hstack([X_tfidf, article_df[[col for col in article_df.columns if '_keywords' in col]].values])

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X_combined, labels_df, test_size=0.2, random_state=42)

# Initialize a multi-output classifier
model = MultiOutputClassifier(LGBMClassifier(n_estimators=200, max_depth=10, class_weight='balanced'))
model.fit(X_train, y_train)

# Predictions on the test set
y_pred = model.predict(X_test)

# Evaluate the model
print(classification_report(y_test, y_pred, target_names=labels_df.columns))
