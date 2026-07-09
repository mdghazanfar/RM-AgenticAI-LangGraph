


import os
import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import get_settings

# Use configured paths from project settings so tests and runtime use the
# same model locations as the rest of the app.
settings = get_settings()
MODEL_PATH = Path(settings.goal_model_path)
ENCODER_PATH = Path(settings.goal_encoders_path)
DATA_PATH = Path(settings.models_dir).parent / "data" / "goal_success_training_dataset.csv"


# --------------------------------------------
# Train the Model (auto-run if missing)
# --------------------------------------------
def train_goal_success_model():
    print("🔁 Training new goal success model...")
    df = pd.read_csv(DATA_PATH)

    # Create two encoders
    exp_encoder = LabelEncoder()
    goal_encoder = LabelEncoder()

    # Encode columns separately
    df['investment_experience_level'] = exp_encoder.fit_transform(df['investment_experience_level'])
    df['goal_success'] = goal_encoder.fit_transform(df['goal_success'])

    X = df[['age', 'annual_income', 'current_savings', 'target_goal_amount',
            'investment_horizon_years', 'number_of_dependents', 'investment_experience_level']]
    y = df['goal_success']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.2f}")

    # Save both encoders together
    encoders = {
        "exp_encoder": exp_encoder,
        "goal_encoder": goal_encoder
    }

    import joblib
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)

    print("✅ Model and encoders saved successfully.")


# --------------------------------------------
# Async Prediction Function
# --------------------------------------------
async def predict_goal_success(goal_data: dict):
    try:
        import joblib
        # Try to load model and encoders from configured paths
        if not MODEL_PATH.exists() or not ENCODER_PATH.exists():
            # Train if missing
            train_goal_success_model()

        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)

        exp_encoder = encoders.get('exp_encoder') or encoders.get('investment_experience_level')

    except Exception as e:
        # On failure, fall back to rule-based prediction
        print(f"⚠️ Model load failed: {e}")
        return {
            "goal_success": "Unknown",
            "probability": 0.5
        }

    try:
        # Encode input categorical field safely
        exp_value = goal_data['investment_experience_level']
        if exp_value not in exp_encoder.classes_:
            print(f"⚠️ '{exp_value}' unseen before, adding it temporarily.")
            exp_encoder.classes_ = np.append(exp_encoder.classes_, exp_value)
        exp_encoded = exp_encoder.transform([exp_value])[0]

        # Prepare features
        features = np.array([[
            goal_data['age'],
            goal_data['annual_income'],
            goal_data['current_savings'],
            goal_data['target_goal_amount'],
            goal_data['investment_horizon_years'],
            goal_data['number_of_dependents'],
            exp_encoded
        ]])

        pred = model.predict(features)[0]
        # Use predict_proba when available
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            # If binary class, take index 1 as success
            prob = float(proba[1]) if len(proba) > 1 else float(proba[0])
        else:
            prob = float(model.predict(features)[0])

        return {
            "goal_success": "Likely" if pred == 1 or prob > 0.6 else "Unlikely",
            "probability": round(prob, 3)
        }

    except Exception as e:
        print(f"⚠️ Prediction failed: {e}")
        return rule_based_prediction(goal_data)


# --------------------------------------------
# Rule-Based Fallback
# --------------------------------------------
def rule_based_prediction(goal_data):
    income = goal_data['annual_income']
    savings = goal_data['current_savings']
    target = goal_data['target_goal_amount']
    years = goal_data['investment_horizon_years']

    total_possible = savings + (income * years * 0.3)

    if total_possible >= target:
        return {"goal_success": "Likely", "probability": 0.8}
    elif total_possible >= 0.7 * target:
        return {"goal_success": "Likely", "probability": 0.6}
    else:
        return {"goal_success": "Unlikely", "probability": 0.3}


# --------------------------------------------
# Auto-Retrain if Model Missing
# --------------------------------------------
def ensure_model_ready():
    if not (MODEL_PATH.exists() and ENCODER_PATH.exists()):
        print("⚙️ Model or encoder not found. Retraining automatically...")
        train_goal_success_model()


# --------------------------------------------
# Example Run
# --------------------------------------------
if __name__ == "__main__":
    ensure_model_ready()

    sample_input = {
        'age': 35,
        'annual_income': 1200000,
        'current_savings': 300000,
        'target_goal_amount': 1000000,
        'investment_horizon_years': 5,
        'number_of_dependents': 2,
        'investment_experience_level': 'Intermediate'
    }

    result = asyncio.run(predict_goal_success(sample_input))
    print("Prediction:", result)
