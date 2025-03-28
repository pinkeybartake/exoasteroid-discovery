# === Dip Classifier Trainer ===
# Trains an AI model (RandomForest) to classify dips based on depth/duration

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

input_csv = "exoasteroid_output/dip_labels_auto.csv"
model_output = "exoasteroid_output/dip_classifier.pkl"

# Load labeled dips
df = pd.read_csv(input_csv)

# Filter only labeled rows
df = df[df['label'].isin(['asteroid', 'planet', 'noise'])]

# Features and labels
X = df[['depth', 'duration']]
y = df['label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))
print("\n=== Confusion Matrix ===")
print(confusion_matrix(y_test, y_pred))

# Save model
joblib.dump(model, model_output)
print(f"\n✅ Model saved to: {model_output}")