from transformers import BertTokenizer, BertModel
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
from scipy.sparse import hstack, vstack
from tqdm import tqdm

from preprocess_articles import preprocess_articles
from settings import label_keywords


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

    mlb = MultiLabelBinarizer()
    synthetic_labels_df = pd.DataFrame(
        mlb.fit_transform([[target] for target in synthetic_targets]),
        columns=mlb.classes_
    )
    
    return synthetic_df, synthetic_labels_df

# Function to count keyword occurrences
def keyword_features(text, keywords):
    return sum(text.count(keyword) for keyword in keywords)

# Dataset class for PyTorch
class ClimateDataset(Dataset):
    def __init__(self, texts, tfidf_features, keyword_features, labels, tokenizer, max_length):
        self.texts = texts
        self.tfidf_features = tfidf_features
        self.keyword_features = keyword_features
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        tfidf = self.tfidf_features[idx].toarray().squeeze(0)  # Convert sparse row to dense
        keywords = self.keyword_features[idx]  # Already dense due to `toarray()` applied earlier
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text, max_length=self.max_length, truncation=True, padding="max_length", return_tensors="pt"
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'tfidf_features': torch.tensor(tfidf, dtype=torch.float),
            'keyword_features': torch.tensor(keywords, dtype=torch.float),
            'labels': torch.tensor(label, dtype=torch.float)
        }

# Model combining transformer embeddings and engineered features
class ClimateModel(nn.Module):
    def __init__(self, transformer_model, tfidf_dim, keyword_dim, num_labels):
        super(ClimateModel, self).__init__()
        self.transformer = transformer_model
        self.transformer_dim = transformer_model.config.hidden_size
        self.fc = nn.Linear(self.transformer_dim + tfidf_dim + keyword_dim, num_labels)
        self.dropout = nn.Dropout(0.3)

    def forward(self, input_ids, attention_mask, tfidf_features, keyword_features):
        # Transformer embeddings
        transformer_output = self.transformer(input_ids=input_ids, attention_mask=attention_mask)
        cls_embeddings = transformer_output.last_hidden_state[:, 0, :]  # CLS token embeddings
        
        # Concatenate features
        combined_features = torch.cat([cls_embeddings, tfidf_features, keyword_features], dim=1)
        
        # Classification
        output = self.fc(self.dropout(combined_features))
        return output


# Preprocess original articles & Prepare synthetic data
article_df, labels_df = preprocess_articles()
synthetic_df, synthetic_labels_df = get_synthetic_sentences()

print("Synthetic Labels Shape:", synthetic_labels_df.shape)
print("Synthetic Labels Sample:", synthetic_labels_df.head())
print("Original Labels Shape:", labels_df.shape)
print("Original Labels Sample:", labels_df.head())

print("Labels DataFrame Values Shape:", labels_df.values.shape)
print("Labels DataFrame Values Sample:", labels_df.values[:5])

# Add keyword-based features
for _, labels in label_keywords.items():
    for label, features in labels.items():
        article_df[label + "_keywords"] = article_df['Text'].apply(lambda x: keyword_features(x.lower(), [f.lower() for f in features]))
        synthetic_df[label + "_keywords"] = synthetic_df['Text'].apply(lambda x: keyword_features(x.lower(), [f.lower() for f in features]))


# Load Data
article_texts = article_df['Text'].tolist()
synthetic_texts = synthetic_df['Text'].tolist()
tfidf_vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_tfidf_real = tfidf_vectorizer.fit_transform(article_texts)
X_tfidf_synthetic = tfidf_vectorizer.transform(synthetic_texts)

article_keywords = article_df[[col for col in article_df.columns if '_keywords' in col]].values
synthetic_keywords = synthetic_df[[col for col in synthetic_df.columns if '_keywords' in col]].values

print("Input to MultiLabelBinarizer (Synthetic):", synthetic_labels_df.values[:5])
print("Input to MultiLabelBinarizer (Original):", labels_df.values[:5])
mlb = MultiLabelBinarizer()
print("Columns:", labels_df.columns)
mlb.fit(labels_df.columns)
labels = mlb.transform(labels_df.values)
synthetic_labels = mlb.transform(synthetic_labels_df.values)
print("Transformed Labels Shape:", labels.shape)
print("Transformed Labels Sample:", labels[:5])
print("Transformed Synthetic Labels Shape:", synthetic_labels.shape)
print("Transformed Synthetic Labels Sample:", synthetic_labels[:5])

print("Original Labels Shape:", labels.shape)
print("Original Labels Sample:", labels[:5])

# Train-test split
X_train, X_test, tfidf_train, tfidf_test, keyword_train, keyword_test, y_train, y_test = train_test_split(
    article_texts, X_tfidf_real, article_keywords, labels, test_size=0.4, random_state=12
)

print("Combined Labels Shape:", np.vstack([y_train, synthetic_labels]).shape)
print("Combined Labels Sample:", np.vstack([y_train, synthetic_labels])[:5])

print("MultiLabelBinarizer Classes:", mlb.classes_)
input()

# Dataset and DataLoader
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
combined_texts = X_train + synthetic_texts
train_dataset = ClimateDataset(combined_texts, 
                                vstack([tfidf_train, X_tfidf_synthetic]), 
                                vstack([keyword_train, synthetic_keywords]).toarray(),
                                np.vstack([y_train, synthetic_labels]),
                                tokenizer, max_length=256)
test_dataset = ClimateDataset(X_test, tfidf_test, keyword_test, y_test, tokenizer, max_length=256)

train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=2, shuffle=False)

# Model setup
transformer = BertModel.from_pretrained('bert-base-uncased')
model = ClimateModel(transformer, tfidf_dim=5000, keyword_dim=article_keywords.shape[1], num_labels=len(mlb.classes_))
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)
criterion = nn.BCEWithLogitsLoss()

# Training Loop
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

epochs = 3
for epoch in range(epochs):
    model.train()
    train_loss = 0.0
    for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        tfidf_features = batch['tfidf_features'].to(device)
        keyword_features = batch['keyword_features'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(input_ids, attention_mask, tfidf_features, keyword_features)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    print(f"Epoch {epoch+1} Loss: {train_loss}")

# Evaluation
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        tfidf_features = batch['tfidf_features'].to(device)
        keyword_features = batch['keyword_features'].to(device)
        labels = batch['labels'].to(device)
        
        outputs = model(input_ids, attention_mask, tfidf_features, keyword_features)
        preds = torch.sigmoid(outputs).cpu().numpy()
        
        all_preds.append(preds)
        all_labels.append(labels.cpu().numpy())

# Flatten and compute metrics
all_preds = np.vstack(all_preds)
all_labels = np.vstack(all_labels)

print("All Labels Shape:", all_labels.shape)  # Should be (num_samples, num_classes)
print("All Predictions Shape:", all_preds.shape)

print("Sample Labels:", all_labels[:5])  # Should be binary vectors
print("Sample Predictions:", (all_preds[:5] > 0.5).astype(int))

# Ensure target names are strings
target_names = [str(cls) for cls in mlb.classes_]
# Generate the classification report
print(classification_report(all_labels, (all_preds > 0.5), target_names=target_names))

torch.save(model, "climate_model_full.pth")
