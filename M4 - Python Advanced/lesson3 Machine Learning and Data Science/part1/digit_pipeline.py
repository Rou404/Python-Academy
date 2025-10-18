"""
Digit Classification Pipeline (Minimal)
--------------------------------------
Steps: acquire → split → normalize → train → validate → serialize → load/predict

Requirements:
    pip install scikit-learn joblib
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib


@dataclass
class Config:
    test_size: float = 0.2
    random_state: int = 42
    model_path: str = "digits_logreg.joblib"
    max_iter: int = 200


def acquire_data():
    """Acquire the digits dataset (8x8 images, 10 classes)."""
    data = load_digits()
    X, y = data.data, data.target  # X: (n_samples, 64) flattened pixels 0..16
    return X.astype(np.float32), y.astype(np.int64)


def split_data(X, y, cfg: Config):
    """Stratified split to preserve class balance."""
    return train_test_split(
        X, y, test_size=cfg.test_size, random_state=cfg.random_state, stratify=y
    )


def normalize_fit_transform(X_train, X_val):
    """Fit scaler on training set only, then transform both sets (avoid leakage)."""
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    return scaler, X_train_scaled, X_val_scaled


def train_model(X_train_scaled, y_train, cfg: Config):
    """Train a simple, strong baseline: multinomial logistic regression."""
    clf = LogisticRegression(
        max_iter=cfg.max_iter,
        multi_class="auto",
        solver="lbfgs",
        n_jobs=None,
    )
    clf.fit(X_train_scaled, y_train)
    return clf


def validate(clf, X_val_scaled, y_val):
    """Evaluate generalization on the hold-out set."""
    y_pred = clf.predict(X_val_scaled)
    acc = accuracy_score(y_val, y_pred)
    print(f"Validation accuracy: {acc:.4f}")
    print("\nClassification report:\n", classification_report(y_val, y_pred))
    print("Confusion matrix:\n", confusion_matrix(y_val, y_pred))
    return acc


def serialize(model, scaler, cfg: Config):
    """Save both model and scaler so inference uses identical preprocessing."""
    bundle = {"model": model, "scaler": scaler}
    joblib.dump(bundle, cfg.model_path)
    print(f"Saved model bundle to: {cfg.model_path}")


def load_and_predict(sample_X, cfg: Config):
    """Load model bundle from disk and run predictions on new data."""
    bundle = joblib.load(cfg.model_path)
    model, scaler = bundle["model"], bundle["scaler"]
    sample_X_scaled = scaler.transform(sample_X)
    return model.predict(sample_X_scaled)


def main():
    cfg = Config()

    # acquire
    X, y = acquire_data()

    # split
    X_train, X_val, y_train, y_val = split_data(X, y, cfg)

    # normalize
    scaler, X_train_sc, X_val_sc = normalize_fit_transform(X_train, X_val)

    # train
    clf = train_model(X_train_sc, y_train, cfg)

    # validate
    validate(clf, X_val_sc, y_val)

    # serialize
    serialize(clf, scaler, cfg)

    # load/predict demo (first 5 samples of validation set)
    demo_preds = load_and_predict(X_val[:5], cfg)
    print("Demo predictions for first 5 validation samples:", demo_preds)
    print("True labels:", y_val[:5])


if __name__ == "__main__":
    main()
