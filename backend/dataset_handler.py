import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class DatasetHandler:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.scaler = StandardScaler()
        self.feature_names = None
        self.label_col = None

        self.dataset = self._load_data()
        self._preprocess()

    # --------------------------------------------------
    # Load dataset
    # --------------------------------------------------
    def _load_data(self):
        if not os.path.isdir(self.dataset_path):
            raise FileNotFoundError("Dataset path must be a folder")

        return self._load_folder()

    def _load_folder(self):
        selected_files = [
            "bot_02-03-2018.csv",
            "ddos-loic-http-loic-udp_20-02-2018.csv"
        ]

        dfs = []

        for file in selected_files:
            path = os.path.join(self.dataset_path, file)

            if not os.path.exists(path):
                print(f"[WARNING] File not found: {file}")
                continue

            print(f"[DatasetHandler] Loading {file}")
            df = pd.read_csv(
                path,
                low_memory=False,
                nrows=200_000   # 🚀 speed fix
            )

            dfs.append(df)

        if not dfs:
            raise RuntimeError("No dataset files loaded")

        return pd.concat(dfs, ignore_index=True)

    # --------------------------------------------------
    # Preprocessing
    # --------------------------------------------------
    def _preprocess(self):
        df = self.dataset.copy()

        # Normalize column names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # 🔍 Robust label detection
        possible_labels = [
            "label",
            "attack",
            "attack_cat",
            "class"
        ]

        for col in possible_labels:
            if col in df.columns:
                self.label_col = col
                break

        if self.label_col is None:
            print("[DEBUG] Available columns:")
            print(df.columns.tolist())
            raise ValueError("Label column not found in dataset")

        print(f"[DatasetHandler] Using label column: '{self.label_col}'")

        # Convert labels → binary
        df[self.label_col] = df[self.label_col].astype(str).apply(
            lambda x: 0 if x.upper() == "BENIGN" else 1
        )

        # Keep numeric features + label
        numeric_df = df.select_dtypes(include=["number"])
        numeric_df[self.label_col] = df[self.label_col]

        # Remove NaN / inf
        numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)
        numeric_df = numeric_df.dropna()

        self.dataset = numeric_df

    # --------------------------------------------------
    # Train / Test Split
    # --------------------------------------------------
    def get_train_test_data(self, test_size=0.2):
        X = self.dataset.drop(columns=[self.label_col])
        y = self.dataset[self.label_col]

        self.feature_names = X.columns.tolist()

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42,
            stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

    # --------------------------------------------------
    # Real-time streaming
    # --------------------------------------------------
    def stream_data(self):
        for _, row in self.dataset.iterrows():
            yield row.drop(self.label_col).to_dict()
