import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import warnings

warnings.filterwarnings('ignore')

def load_model_and_vectorizer():
    """
    Load the trained phishing detection model and vectorizer from pickle files.
    """
    try:
        with open("models/phishing_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("models/vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception as e:
        print(f"[ERROR] Failed to load model/vectorizer: {e}")
        raise

def predict_phishing(model, vectorizer, text):
    """
    Predict whether a given text is phishing or not using the loaded model and vectorizer.
    """
    vectorized = vectorizer.transform([text])
    prediction = model.predict(vectorized)
    return prediction[0]

if __name__ == "__main__":
    # Step 1: Load the dataset
    url = "https://drive.google.com/uc?id=1b973kuaY7jQRSLzOExbgFb_rf97Nyc4v"
    try:
        df = pd.read_csv(url, encoding='latin1')
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        exit(1)

    df.drop_duplicates(inplace=True)
    df.drop(columns=[col for col in ["Unnamed: 2", "Unnamed: 3", "Unnamed: 4"] if col in df.columns], inplace=True)

    label_encoder = LabelEncoder()
    df['v1'] = label_encoder.fit_transform(df['v1'])  # 0 = ham, 1 = spam

    print("=== Dataset Preview ===")
    print(df.head())
    print("\n" + "="*50 + "\n")

    # Step 2: Prepare features and labels
    X = df['v2']
    y = df['v1']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer()
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # Step 3: KNN with Grid Search
    knn_params = {
        'n_neighbors': [3, 5, 7, 9],
        'metric': ['euclidean', 'manhattan']
    }

    knn_grid = GridSearchCV(KNeighborsClassifier(), knn_params, cv=5, scoring='accuracy')
    knn_grid.fit(X_train_tfidf, y_train)

    print(f"[KNN] Best Parameters: {knn_grid.best_params_}")
    best_knn = knn_grid.best_estimator_

    knn_predictions = best_knn.predict(X_test_tfidf)
    print("[KNN] Classification Report:")
    print(classification_report(y_test, knn_predictions))
    print(f"[KNN] Accuracy: {accuracy_score(y_test, knn_predictions)}")
    print("\n" + "="*50 + "\n")

    # Step 4: Logistic Regression
    log_model = LogisticRegression()
    log_model.fit(X_train_tfidf, y_train)
    log_predictions = log_model.predict(X_test_tfidf)

    print("[Logistic Regression] Classification Report:")
    print(classification_report(y_test, log_predictions))
    print(f"[Logistic Regression] Accuracy: {accuracy_score(y_test, log_predictions)}")
    print("\n" + "="*50 + "\n")

    # Step 5: MLP Classifier (Final Model)
    mlp_model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=1000, random_state=42)
    mlp_model.fit(X_train_tfidf, y_train)
    mlp_predictions = mlp_model.predict(X_test_tfidf)

    print("[MLP Classifier] Classification Report:")
    print(classification_report(y_test, mlp_predictions))
    print(f"[MLP] Accuracy: {accuracy_score(y_test, mlp_predictions)}")
    print("\n" + "="*50 + "\n")

    # Step 6: Save model and vectorizer
    try:
        with open("models/phishing_model.pkl", "wb") as f:
            pickle.dump(mlp_model, f)

        with open("models/vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)

        print("Model and vectorizer were saved successfully using pickle.")
    except Exception as e:
        print(f"[ERROR] Failed to save model/vectorizer: {e}")
