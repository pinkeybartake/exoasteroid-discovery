from fastapi import FastAPI
import subprocess

app = FastAPI(title="ExoAsteroid Discovery API 🚀")

@app.get("/")
def root():
    return {"message": "ExoAsteroid Pipeline Ready!"}

@app.post("/detect-dips")
def detect_dips():
    subprocess.run(["python", "scripts/batch_dip_scanner.py"])
    return {"status": "✅ Dips detected and saved."}

@app.post("/auto-label")
def auto_label():
    subprocess.run(["python", "scripts/auto_label_dips.py"])
    return {"status": "✅ Auto-labeling complete."}

@app.post("/train-model")
def train_model():
    subprocess.run(["python", "scripts/train_dip_classifier.py"])
    return {"status": "✅ Model trained and saved."}

@app.post("/predict")
def predict():
    subprocess.run(["python", "scripts/predict_dip_labels.py"])
    return {"status": "✅ New dips labeled with predictions."}

@app.post("/full-run")
def full_pipeline():
    subprocess.run(["python", "scripts/batch_dip_scanner.py"])
    subprocess.run(["python", "scripts/auto_label_dips.py"])
    subprocess.run(["python", "scripts/train_dip_classifier.py"])
    subprocess.run(["python", "scripts/predict_dip_labels.py"])
    return {"status": "🚀 Full pipeline complete."}
