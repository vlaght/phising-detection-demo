from typing import Literal
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def predict_phishing(model: RandomForestClassifier, features: dict):
    """
    Predict if a website is phishing based on features

    Args:
        model: Trained classifier model
        features: Dictionary with feature values

    Returns:
        tuple: (prediction, prediction_probabilities)
    """
    # Convert features to DataFrame
    df = pd.DataFrame([features])

    # Ensure correct data types
    df["google_index"] = df["google_index"].astype(bool)
    df["page_rank"] = df["page_rank"].astype("int64")
    df["nb_hyperlinks"] = df["nb_hyperlinks"].astype("int64")
    df["web_traffic"] = df["web_traffic"].astype("int64")
    df["nb_www"] = df["nb_www"].astype("int64")
    df["domain_age"] = df["domain_age"].astype("int64")
    df["longest_word_path"] = df["longest_word_path"].astype("int64")
    df["ratio_extHyperlinks"] = df["ratio_extHyperlinks"].astype("float64")
    df["ratio_intHyperlinks"] = df["ratio_intHyperlinks"].astype("float64")
    df["phish_hints"] = df["phish_hints"].astype("int64")

    # Make prediction
    prediction: Literal[0, 1] = model.predict(df)[0]
    prediction_proba = model.predict_proba(df)[0]

    return prediction, prediction_proba
