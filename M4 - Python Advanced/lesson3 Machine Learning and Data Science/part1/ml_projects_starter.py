"""
ML Projects Starter (Scaffolds & TODOs)
--------------------------------------
Each section is a classic exercise with guidance. Keep imports minimal.

General advice:
- Start with a simple baseline (logistic/linear model).
- Use train/validation/test or cross-validation.
- Save your preprocessing with the model for reuse.
"""

from __future__ import annotations
from dataclasses import dataclass

import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier

# Optional: uncomment if you want to fetch from Hugging Face (requires: pip install datasets)
# from datasets import load_dataset

# Optional: Kaggle download tips (requires: pip install kaggle; set up API token in ~/.kaggle/kaggle.json)
# Example CLI (run in terminal, not Python):
# kaggle datasets download -d uciml/iris
# unzip iris.zip

@dataclass
class SplitCfg:
    test_size: float = 0.2
    random_state: int = 42


def standard_split(X, y, cfg: SplitCfg):
    return train_test_split(X, y, test_size=cfg.test_size, random_state=cfg.random_state, stratify=y if len(np.unique(y))>2 else None)


# 1) Iris Classification (classic small dataset)
def iris_classification():
    from sklearn.datasets import load_iris
    data = load_iris()
    X, y = data.data.astype(np.float32), data.target

    X_tr, X_te, y_tr, y_te = standard_split(X, y, SplitCfg())
    scaler = StandardScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_te_s = scaler.transform(X_te)

    clf = LogisticRegression(max_iter=200).fit(X_tr_s, y_tr)
    y_pred = clf.predict(X_te_s)
    print("Iris accuracy:", accuracy_score(y_te, y_pred))


# 2) Handwritten Digits (alternate model exploration)
def digits_experiments():
    from sklearn.datasets import load_digits
    X, y = load_digits(return_X_y=True)
    X = X.astype(np.float32)

    X_tr, X_te, y_tr, y_te = standard_split(X, y, SplitCfg())
    scaler = StandardScaler().fit(X_tr)
    X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)

    # TODO: try different models (uncomment to experiment)
    clf = LogisticRegression(max_iter=200).fit(X_tr_s, y_tr)
    # clf = RandomForestClassifier(n_estimators=200, random_state=0).fit(X_tr, y_tr)

    y_pred = clf.predict(X_te_s)
    print("Digits accuracy:", accuracy_score(y_te, y_pred))


# 3) IMDB Sentiment (Hugging Face) – text classification
def imdb_sentiment_hf():
    """
    Optional (requires: pip install datasets). Illustrates HF datasets integration.
    Convert text to simple bag-of-words or TF-IDF (scikit-learn) for a light baseline.
    """
    # from datasets import load_dataset
    # from sklearn.feature_extraction.text import TfidfVectorizer
    # ds = load_dataset("imdb")
    # train_texts = ds["train"]["text"]
    # train_labels = np.array(ds["train"]["label"])
    # test_texts = ds["test"]["text"]
    # test_labels = np.array(ds["test"]["label"])
    # vec = TfidfVectorizer(max_features=20000)
    # X_tr = vec.fit_transform(train_texts)
    # X_te = vec.transform(test_texts)
    # clf = LogisticRegression(max_iter=300).fit(X_tr, train_labels)
    # print("IMDB accuracy:", clf.score(X_te, test_labels))
    pass


# 4) House Prices Regression (Kaggle) – structured regression
def house_prices_kaggle():
    """
    Steps:
    - Download 'house-prices-advanced-regression-techniques' via Kaggle CLI.
    - Load CSV with pandas, select numeric features, impute missing values.
    - Train LinearRegression; evaluate with MAE.
    """
    # import pandas as pd
    # train = pd.read_csv("train.csv")
    # y = train["SalePrice"].values.astype(np.float32)
    # X = train.select_dtypes(include=[np.number]).drop(columns=["SalePrice"]).fillna(0.0).values.astype(np.float32)
    # X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
    # scaler = StandardScaler().fit(X_tr)
    # X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)
    # model = LinearRegression().fit(X_tr_s, y_tr)
    # pred = model.predict(X_te_s)
    # print("House Prices MAE:", mean_absolute_error(y_te, pred))
    pass


# 5) Wine Quality (UCI) – classification or regression
def wine_quality():
    """
    Download CSV (red or white), then:
    - Choose classification (quality >= 6) or regression (predict quality score).
    """
    # import pandas as pd
    # df = pd.read_csv("winequality-red.csv", sep=";")
    # y = (df["quality"] >= 6).astype(int).values
    # X = df.drop(columns=["quality"]).values.astype(np.float32)
    # X_tr, X_te, y_tr, y_te = standard_split(X, y, SplitCfg())
    # scaler = StandardScaler().fit(X_tr)
    # X_tr_s, X_te_s = scaler.transform(X_tr), scaler.transform(X_te)
    # clf = RandomForestClassifier(n_estimators=300, random_state=0).fit(X_tr_s, y_tr)
    # print("Wine F1:", f1_score(y_te, clf.predict(X_te_s)))
    pass


if __name__ == "__main__":
    # Run one or more to test locally
    iris_classification()
    digits_experiments()
    # imdb_sentiment_hf()  # requires datasets + internet
    # house_prices_kaggle()  # requires local CSVs from Kaggle
    # wine_quality()
