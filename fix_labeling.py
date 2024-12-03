import json

# Define the updated, more granular grouping of labels
label_mapping = {
    "causes": {
        "Energy and Industry": [
            "Fossil Fuels", "Energy Use", "Industrial Activity", "Transportation"
        ],
        "Land Use and Agriculture": [
            "Deforestation", "Agriculture",
        ],
        "Governance and Policy Failures": [
            "Governance and Policy Failures"
        ]
    },
    "consequences": {
        "Environmental Effects": [
            "Global Warming and Extreme Weather", "Ocean Changes and Rising Sea Levels", 
            "Ecosystem Disruption and Biodiversity Loss", "Environmental Degradation and Air Quality Issues", 
            "Air Pollution"
        ],
        "Human and Health Effects": [
            "Food and Water Scarcity", "Economic and Health Impacts", "Migration and Displacement", "Global Economy"
        ],
    },
    "solutions": {
        "Technological Solutions": [
            "Renewable Energy and Efficiency", "Electric Vehicles", "Sustainable Solutions"
        ],
        "Governance and Policy": [
            "Climate Governance and Policy", "International Cooperation and Awareness", 
            "Green Jobs Creation", "Climate Investments"
        ],
        "Adaptation and Resilience": [
            "Sustainable Agriculture and Land Use", "Waste Management and Reduction", 
            "Transportation Solutions", "Resilient Infrastructure"
        ]
    },
}

# Reverse the mapping to create a label-to-category dictionary
label_to_category = {}

# Loop through the categories and their subcategories
for category, subcategories in label_mapping.items():
    for subcategory, labels in subcategories.items():
        for label in labels:
            label_to_category[label] = f"{subcategory}"

# Function to transform article labels to their broader categories
def transform_labels(labels):
    transformed = set()
    for label in labels:
        # Get the category or default to 'Unrelated' if not found
        category = label_to_category.get(label, "Unrelated")
        if category == "Unrelated":
            print(label)
        transformed.add(category)
    return list(transformed)

# Read the articles.json file
with open("data/article_labels_old.json", 'r') as file:
    data = json.load(file)

# Update the articles with the transformed labels
for article_id, article_labels in data['articles'].items():
    updated_labels = transform_labels(article_labels)
    data['articles'][article_id] = updated_labels

# Write the updated content to articles_new.json
with open('data/article_labels.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

print("The labels have been updated and written to articles_new.json.")
