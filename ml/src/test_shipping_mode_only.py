
from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "raw" /
    "syndelay-main" / "data" / "syndelay_v1.csv"
)

df = pd.read_csv(DATA_PATH)

# Use only shipping_mode
X = df[["shipping_mode"]]
y = df["label"]

# Same split and random seed as our previous experiments
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50,
    stratify=y_temp, random_state=42
)

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["shipping_mode"])
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ))
])

print("Training shipping-mode-only model...")
model.fit(X_train, y_train)

y_pred = model.predict(X_val)

print("\nSHIPPING MODE ONLY - VALIDATION RESULTS")
print("Accuracy:", round(accuracy_score(y_val, y_pred), 4))
print("Macro F1:", round(f1_score(y_val, y_pred, average="macro"), 4))
print("Weighted F1:", round(f1_score(y_val, y_pred, average="weighted"), 4))

print("\nCLASSIFICATION REPORT")
print(classification_report(y_val, y_pred, zero_division=0))

print("CONFUSION MATRIX")
print(confusion_matrix(y_val, y_pred))
