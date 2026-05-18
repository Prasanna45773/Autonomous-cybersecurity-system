from sklearn.ensemble import RandomForestClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import numpy as np
import os
import pandas as pd

class DetectionAgent:
    def __init__(self):
        # Supervised models
        self.random_forest = RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        )
        self.xgboost = XGBClassifier(
            n_estimators=100,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        self.logistic = LogisticRegression(
            max_iter=1000, random_state=42, n_jobs=-1
        )

        # Unsupervised anomaly detector
        self.isolation_forest = IsolationForest(
            contamination=0.1, random_state=42
        )

        self.models_trained = False
        self.feature_names = None

    # --------------------------------------------------
    # Training
    # --------------------------------------------------
    def train(self, X_train, y_train, feature_names):
        """
        X_train: scaled numpy array
        y_train: labels
        feature_names: column order from DatasetHandler
        """
        print("[DetectionAgent] Training detection models...")

        self.feature_names = feature_names

        print("  - Random Forest")
        self.random_forest.fit(X_train, y_train)

        print("  - XGBoost")
        self.xgboost.fit(X_train, y_train)

        print("  - Logistic Regression")
        self.logistic.fit(X_train, y_train)

        print("  - Isolation Forest")
        self.isolation_forest.fit(X_train)

        self.models_trained = True
        print("[DetectionAgent] All models trained successfully")

    # --------------------------------------------------
    # Real-time detection (single data row)
    # --------------------------------------------------
    def detect(self, data_row, scaler):
        """
        data_row: dict from MonitoringAgent
        scaler: fitted StandardScaler from DatasetHandler
        """
        if not self.models_trained:
            raise Exception("Models not trained")

        # Ensure correct feature order
        x = np.array([data_row[f] for f in self.feature_names]).reshape(1, -1)
        x_df = pd.DataFrame(x, columns=self.feature_names)
        x_scaled = scaler.transform(x_df)


        # Individual model predictions
        rf_pred = self.random_forest.predict(x_scaled)[0]
        xgb_pred = self.xgboost.predict(x_scaled)[0]
        lr_pred = self.logistic.predict(x_scaled)[0]

        iso_pred = 1 if self.isolation_forest.predict(x_scaled)[0] == -1 else 0

        votes = np.array([rf_pred, xgb_pred, lr_pred, iso_pred])
        final_prediction = 1 if np.sum(votes) >= 2 else 0

        # Confidence from supervised models
        rf_conf = max(self.random_forest.predict_proba(x_scaled)[0])
        xgb_conf = max(self.xgboost.predict_proba(x_scaled)[0])
        lr_conf = max(self.logistic.predict_proba(x_scaled)[0])

        confidence = np.mean([rf_conf, xgb_conf, lr_conf])

        return final_prediction, confidence

    # --------------------------------------------------
    # Batch prediction (evaluation)
    # --------------------------------------------------
    def predict(self, X):
        if not self.models_trained:
            raise Exception("Models not trained")

        rf_pred = self.random_forest.predict(X)
        xgb_pred = self.xgboost.predict(X)
        lr_pred = self.logistic.predict(X)
        iso_pred = np.where(self.isolation_forest.predict(X) == -1, 1, 0)

        predictions = np.array([rf_pred, xgb_pred, lr_pred, iso_pred])

        final_pred = np.apply_along_axis(
            lambda x: 1 if np.sum(x) >= 2 else 0,
            axis=0,
            arr=predictions
        )

        return final_pred

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------
    def evaluate(self, X_test, y_test):
        predictions = self.predict(X_test)

        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, zero_division=0),
            'recall': recall_score(y_test, predictions, zero_division=0),
            'f1_score': f1_score(y_test, predictions, zero_division=0)
        }

    # --------------------------------------------------
    # Save / Load
    # --------------------------------------------------
    def save_models(self, path='models/'):
        os.makedirs(path, exist_ok=True)

        joblib.dump(self.random_forest, f'{path}random_forest.pkl')
        joblib.dump(self.xgboost, f'{path}xgboost.pkl')
        joblib.dump(self.logistic, f'{path}logistic.pkl')
        joblib.dump(self.isolation_forest, f'{path}isolation_forest.pkl')
        joblib.dump(self.feature_names, f'{path}feature_names.pkl')

        print(f"[DetectionAgent] Models saved to {path}")

    def load_models(self, path='models/'):
        self.random_forest = joblib.load(f'{path}random_forest.pkl')
        self.xgboost = joblib.load(f'{path}xgboost.pkl')
        self.logistic = joblib.load(f'{path}logistic.pkl')
        self.isolation_forest = joblib.load(f'{path}isolation_forest.pkl')
        self.feature_names = joblib.load(f'{path}feature_names.pkl')

        self.models_trained = True
        print(f"[DetectionAgent] Models loaded from {path}")
