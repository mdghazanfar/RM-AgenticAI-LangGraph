


"""Main ML model training orchestration."""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import get_settings, get_logger

logger = get_logger("train_models")


def create_training_data():
    """Create synthetic training data."""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'age': np.random.randint(25, 65, n_samples),
        'annual_income': np.random.randint(300000, 2000000, n_samples),
        'current_savings': np.random.randint(50000, 1000000, n_samples),
        'target_goal_amount': np.random.randint(500000, 5000000, n_samples),
        'investment_horizon_years': np.random.randint(3, 20, n_samples),
        'number_of_dependents': np.random.randint(0, 4, n_samples),
        'investment_experience_level': np.random.choice(
            ['Beginner', 'Intermediate', 'Advanced'], n_samples, p=[0.4, 0.4, 0.2]
        )
    }
    
    df = pd.DataFrame(data)
    
    # Generate risk labels
    df['risk_profile'] = 'Moderate'
    
    high_risk = (
        (df['age'] < 40) & (df['annual_income'] > 1000000) &
        (df['investment_horizon_years'] > 10) &
        (df['investment_experience_level'] == 'Advanced')
    )
    df.loc[high_risk, 'risk_profile'] = 'High'
    
    low_risk = (
        (df['age'] > 50) & (df['annual_income'] < 800000) &
        (df['investment_horizon_years'] < 5) |
        (df['investment_experience_level'] == 'Beginner')
    )
    df.loc[low_risk, 'risk_profile'] = 'Low'
    
    return df


def train_risk_model():
    """Train risk profile model."""
    logger.info("Training risk profile model...")
    settings = get_settings()
    
    df = create_training_data()
    
    features = ['age', 'annual_income', 'current_savings', 'target_goal_amount',
                'investment_horizon_years', 'number_of_dependents', 
                'investment_experience_level']
    
    X = df[features].copy()
    y = df['risk_profile']
    
    # Encode categorical
    label_encoders = {}
    for col in features:
        if not pd.api.types.is_numeric_dtype(X[col].dtype):
            le = LabelEncoder()
            X[col] = np.asarray(le.fit_transform(X[col].astype(str)))
            label_encoders[col] = le
    
    # Encode target
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(y)
    label_encoders['risk_profile'] = target_encoder
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )
    
    # Train
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Risk model accuracy: {accuracy:.3f}")
    
    # Save
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, settings.risk_model_path)
    joblib.dump(label_encoders, settings.risk_encoders_path)
    logger.info(f"Saved to {settings.risk_model_path}")
    
    return True


def train_goal_model():
    """Train goal success model."""
    logger.info("Training goal success model...")
    settings = get_settings()
    
    df = create_training_data()
    
    features = ['age', 'annual_income', 'current_savings', 'target_goal_amount',
                'investment_horizon_years', 'number_of_dependents', 'investment_experience_level']
    
    X = df[features].copy()
    
    # Create target
    savings_ratio = df['current_savings'] / df['target_goal_amount']
    y = ((savings_ratio > 0.4) & (df['investment_horizon_years'] >= 10)).astype(int)
    
    # Encode categorical
    label_encoders = {}
    for col in features:
        if not pd.api.types.is_numeric_dtype(X[col].dtype):
            le = LabelEncoder()
            X[col] = np.asarray(le.fit_transform(X[col].astype(str)))
            label_encoders[col] = le
            # Add exp_encoder alias for compatibility
            if col == 'investment_experience_level':
                label_encoders['exp_encoder'] = le
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = accuracy_score(y_test, model.predict(X_test))
    logger.info(f"Goal model accuracy: {accuracy:.3f}")
    
    # Save
    joblib.dump(model, settings.goal_model_path)
    joblib.dump(label_encoders, settings.goal_encoders_path)
    logger.info(f"Saved to {settings.goal_model_path}")
    
    return True


def main():
    """Main training function."""
    logger.info("Starting model training...")
    
    try:
        risk_success = train_risk_model()
        goal_success = train_goal_model()
        
        if risk_success and goal_success:
            logger.info("✅ All models trained successfully")
            return True
        else:
            logger.error("❌ Training failed")
            return False
    except Exception as e:
        logger.error(f"Training error: {e}")
        return False


if __name__ == "__main__":
    main()
