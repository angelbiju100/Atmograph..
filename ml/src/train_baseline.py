
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
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

MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

# 1. Load dataset
df = pd.read_csv(DATA_PATH)

# 2. Derive calendar features from order date
order_datetime = pd.to_datetime(
    df["order_date"],
    unit="D",
    origin="1899-12-30"
)

df["order_month"] = order_datetime.dt.month
df["order_day_of_week"] = order_datetime.dt.day_of_week

# 3. Select prediction features
numeric_features = [
    "order_month",
    "order_day_of_week",
    "latitude",
    "longitude",
    "customer_zipcode",
    "order_item_discount",
    "order_item_discount_rate",
    "order_item_product_price",
    "order_item_quantity",
    "product_price"
]

categorical_features = [
    "payment_type",
    "category_name",
    "customer_city",
    "customer_country",
    "customer_segment",
    "customer_state",
    "department_name",
    "market",
    "order_city",
    "order_country",
    "order_region",
    "order_state",
    "product_name"
]

features = numeric_features + categorical_features

X = df[features]
y = df["label"]

# 4. Stratified train / validation / test split
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)

print("DATA SPLIT")
print("Training:", len(X_train))
print("Validation:", len(X_val))
print("Testing:", len(X_test))

# 5. Preprocessing
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features)
])

# 6. Random Forest
classifier = RandomForestClassifier(
    n_estimators=200,
    max_features="sqrt",
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",
    n_jobs=-1,
    random_state=42
)

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", classifier)
])

# 7. Train
print("\nTraining Random Forest...")
model.fit(X_train, y_train)

# 8. Validation evaluation
y_pred = model.predict(X_val)

accuracy = accuracy_score(y_val, y_pred)
macro_f1 = f1_score(y_val, y_pred, average="macro")
weighted_f1 = f1_score(y_val, y_pred, average="weighted")

print("\nVALIDATION RESULTS")
print("=" * 40)
print(f"Accuracy: {accuracy:.4f}")
print(f"Macro F1: {macro_f1:.4f}")
print(f"Weighted F1: {weighted_f1:.4f}")

print("\nCLASSIFICATION REPORT")
print(classification_report(y_val, y_pred, zero_division=0))

print("\nCONFUSION MATRIX")
print(confusion_matrix(y_val, y_pred))

# 9. Save model
joblib.dump(model, MODEL_DIR / "random_forest_without_shipping_mode.joblib")

# 10. Save validation results
results = {
    "model": "Random Forest",
    "random_state": 42,
    "training_records": len(X_train),
    "validation_records": len(X_val),
    "test_records_reserved": len(X_test),
    "accuracy": accuracy,
    "macro_f1": macro_f1,
    "weighted_f1": weighted_f1,
    "features": features
}

with open(REPORT_DIR / "baseline_without_shipping_mode.json", "w") as file:
    json.dump(results, file, indent=4)

print("\nModel saved successfully.")
print("Validation report saved successfully.")
print("Test data has been reserved for final evaluation.")
