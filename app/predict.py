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

def predict_burnout(avg_tired: float, avg_capable: float, avg_meaningful: float):
    """
    Predict burnout risk using the Logistic Regression model with proper scaling.

    Args:
        avg_tired (float): Average tiredness score
        avg_capable (float): Average capability score
        avg_meaningful (float): Average meaningfulness score

    Returns:
        dict: {
            "burnout_risk": bool,
            "confidence": float,
            "label": str,
            "model_version": str
        }
    """
    data = np.array([[avg_tired, avg_capable, avg_meaningful]])

    # Scale input
    scaled = scaler.transform(data)

    # Predict encoded class label
    encoded_pred = lr.predict(scaled)[0]

    # Decode to actual label (e.g., "Low", "Moderate", "High")
    label = label_enc.inverse_transform([encoded_pred])[0]

    # Get class probabilities
    proba = lr.predict_proba(scaled)[0]
    confidence = float(np.max(proba))

    return {
        "burnout_risk": label.lower() == "high",
        "label": label,
        "confidence": confidence,
        "model_version": "logistic_regression"
    }
