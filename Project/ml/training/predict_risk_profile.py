# TODO: Import numpy, pickle for model loading
# TODO: Import settings for model paths
# TODO: Create async predict_risk_profile function accepting prospect features
# TODO: Load risk model and LabelEncoder from disk or use defaults
# TODO: Prepare features array from prospect data
# TODO: Call model.predict and model.predict_proba
# TODO: Extract risk level and confidence score
# TODO: Create fallback rule-based prediction if model unavailable:
#   - Check age, income, savings, investment experience
#   - Apply investment rules to determine risk level
# TODO: Return (risk_level, confidence_score) tuple
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from config import get_settings
from pathlib import Path

# ----------------------------
# Paths and Settings
# ----------------------------
settings = get_settings()
MODEL_PATH = Path(settings.risk_model_path)
ENCODER_PATH = Path(settings.risk_encoders_path)
DATA_PATH = Path(settings.models_dir).parent / "data" / "risk_profile_training_dataset.csv"

# ----------------------------
# Train and Save Model (only once)
# ----------------------------
def train_risk_model():
    data = pd.read_csv(DATA_PATH)

    feature_columns = [
        "age",
        "annual_income",
        "current_savings",
        "target_goal_amount",
        "investment_horizon_years",
        "number_of_dependents",
        "investment_experience_level"
    ]

    X = data[feature_columns].copy()
    y = data["risk_profile"]

    # Encode 'investment_experience_level' (categorical) to numeric
    exp_encoder = LabelEncoder()
    X["investment_experience_level"] = exp_encoder.fit_transform(X["investment_experience_level"])

    # Encode target labels
    risk_encoder = LabelEncoder()
    y_encoded = risk_encoder.fit_transform(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # Train RandomForest model
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Model trained successfully. Accuracy: {acc:.2f}")

    # Save model and label encoders
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    encoders = {
        "investment_experience_level": exp_encoder,
        "risk_profile": risk_encoder
    }
    joblib.dump(encoders, ENCODER_PATH)

    print(f"✅ Model saved at: {MODEL_PATH}")
    print(f"✅ Encoders saved at: {ENCODER_PATH}")

# ----------------------------
# Async Prediction Function
# ----------------------------
async def predict_risk_profile(prospect_features: dict):
    """
    Predicts the risk profile based on prospect features.
    """
    try:
        # Load model and encoders
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)
        exp_encoder = encoders["investment_experience_level"]
        risk_encoder = encoders["risk_profile"]

        # Encode investment experience
        exp_level_value = prospect_features["investment_experience_level"]
        try:
            exp_level_encoded = exp_encoder.transform([exp_level_value])[0]
        except ValueError:
            # Unknown category → assign default
            exp_level_encoded = 0

        X_input = np.array([[prospect_features["age"],
                             prospect_features["annual_income"],
                             prospect_features["current_savings"],
                             prospect_features.get("target_goal_amount", 0),
                             prospect_features["investment_horizon_years"],
                             prospect_features["number_of_dependents"],
                             exp_level_encoded]])

        prediction = model.predict(X_input)[0]
        probabilities = model.predict_proba(X_input)[0]

        risk_level = risk_encoder.inverse_transform([prediction])[0]
        confidence_score = float(np.max(probabilities))

        return risk_level, confidence_score

    except Exception as e:
        print(f"⚠️ Model prediction failed, using fallback rules. Error: {e}")

        # ----------------------------
        # Fallback Rule-based Logic
        # ----------------------------
        age = prospect_features.get("age", 30)
        income = prospect_features.get("annual_income", 50000)
        savings = prospect_features.get("current_savings", 10000)
        exp = prospect_features.get("investment_experience_level", "Beginner")

        # Simple heuristic
        if isinstance(exp, str) and exp.lower() in ["advanced", "expert"]:
            risk_level = "High"
        elif income > 60000 and savings > 20000:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        confidence_score = 0.6
        return risk_level, confidence_score


# ----------------------------
# Run Training Once
# ----------------------------
if __name__ == "__main__":
    train_risk_model()

    import asyncio

    # Example prediction
    prospect_data = {
        "age": 30,
        "annual_income": 80000,
        "current_savings": 20000,
        "investment_horizon_years": 5,
        "number_of_dependents": 1,
        "investment_experience_level": "Intermediate"
    }

    risk, confidence = asyncio.run(predict_risk_profile(prospect_data))
    print(f"Predicted Risk Level: {risk}, Confidence: {confidence:.2f}")
