import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# 1) LOAD TRAINING DATA
df = pd.read_csv("../data_processed/training_data.csv")
print("Original rows:", len(df))

# 2) DROP ROWS WITH MISSING VALUES IN KEY COLUMNS
df = df.dropna(subset=["class1", "class2", "severity"])
print("Rows after dropping NA:", len(df))

# 3) ENCODE TEXT LABELS AS NUMBERS
class_encoder = LabelEncoder()
severity_encoder = LabelEncoder()

df["class1_enc"] = class_encoder.fit_transform(df["class1"].astype(str))
df["class2_enc"] = class_encoder.fit_transform(df["class2"].astype(str))
df["severity_enc"] = severity_encoder.fit_transform(df["severity"].astype(str))

X = df[["class1_enc", "class2_enc"]]
y = df["severity_enc"]

# 4) TRAIN / TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Train size:", len(X_train), "Test size:", len(X_test))

# 5) TRAIN RANDOM FOREST MODEL
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    random_state=42,
)
model.fit(X_train, y_train)

# 6) EVALUATION
y_pred = model.predict(X_test)

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))

print("\n=== Confusion Matrix ===")
print(confusion_matrix(y_test, y_pred))

# 7) SAVE MODEL & ENCODERS FOR LATER USE
joblib.dump(model, "../data_processed/rf_interaction_model.joblib")
joblib.dump(class_encoder, "../data_processed/class_encoder.joblib")
joblib.dump(severity_encoder, "../data_processed/severity_encoder.joblib")
print("\nSaved model and encoders to data_processed/")
