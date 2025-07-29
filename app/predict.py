import joblib
import numpy as np
import os

# Resolve model paths relative to the current file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model", "output")

# Load all models and artifacts
lr = joblib.load(os.path.join(MODEL_DIR, "logistic_regression_model.pkl"))
rf = joblib.load(os.path.join(MODEL_DIR, "random_forest_model.pkl"))
xgb = joblib.load(os.path.join(MODEL_DIR, "xgboost_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "burnout_scaler.pkl"))
label_enc = joblib.load(os.path.join(MODEL_DIR, "burnout_label_encoder.pkl"))

def predict_burnout(avg_tired, avg_capable, avg_meaningful):
    """
    Predict burnout risk using the XGBoost model.
    Also uses scaled features where needed.

    Args:
        avg_tired (float): Average tiredness score
        avg_capable (float): Average capability score
        avg_meaningful (float): Average meaningfulness score

    Returns:
        dict: Prediction result including risk, confidence, and model version
    """
    data = np.array([[avg_tired, avg_capable, avg_meaningful]])

    # Predict using all models (optional if you want to compare)
    scaled = scaler.transform(data)
    predictions = {
        "lr": lr.predict(scaled)[0],
        "rf": rf.predict(data)[0],
        "xgb": xgb.predict(data)[0]
    }

    # Final prediction from XGBoost
    encoded = predictions["xgb"]
    label = label_enc.inverse_transform([encoded])[0]
    confidence = float(np.max(xgb.predict_proba(data)))

    return {
        "burnout_risk": label.lower() == "high",
        "confidence": confidence,
        "model_version": "xgboost"
    }
