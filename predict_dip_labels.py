# === Predict Dip Labels for New Data ===
# Loads a trained model and applies it to unlabeled dips

import pandas as pd
import joblib
import os

# Paths
model_path = "exoasteroid_output/dip_classifier.pkl"
new_data_path = "exoasteroid_output/all_dips.csv"
predicted_output_path = "exoasteroid_output/predicted_dip_labels.csv"

# Load model
if not os.path.exists(model_path):
    raise FileNotFoundError("❌ Model not found. Please run train_dip_classifier.py first.")

model = joblib.load(model_path)
print("✅ Loaded trained dip classifier")

# Load new dips
df = pd.read_csv(new_data_path)
X_new = df[['depth', 'duration']]

# Predict labels
predictions = model.predict(X_new)
df['predicted_label'] = predictions

# Save results
df.to_csv(predicted_output_path, index=False)
print(f"✅ Predicted labels saved to: {predicted_output_path}")
