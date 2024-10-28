from preprocess_articles import preprocess_articles
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer


article_df, labels_df = preprocess_articles()

# Convert cleaned text to TF-IDF features
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(article_df['Text'])

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, labels_df, test_size=2, random_state=42)

# Initialize a multi-output classifier
model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100))

# Train the model
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mlb = MultiLabelBinarizer()
print(classification_report(y_test, y_pred, target_names=mlb.classes))
