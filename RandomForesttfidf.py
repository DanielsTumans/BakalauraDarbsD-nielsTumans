import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

category_files = {
    "Auto.txt": "Auto",
    "Bizness.txt": "Bizness",
    "Kultura.txt": "Kultura",
    "Life.txt": "Life",
    "Sports.txt": "Sport"
}

data_dir = "Data_set_1"
data = []
labels = []

for filename, label in category_files.items():
    path = os.path.join(data_dir, filename)
    with open(path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
        data.extend(lines)
        labels.extend([label] * len(lines))

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

vectorizer = joblib.load("tfidf_vectorizer.pkl")
X_train_vec = vectorizer.transform(X_train)
X_test_vec = vectorizer.transform(X_test)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_vec, y_train)

y_pred = rf_model.predict(X_test_vec)
print("\nClassification (Random Forest):")
print(classification_report(y_test, y_pred))

joblib.dump(rf_model, "random_forest_model.pkl")
print("Model saved 'random_forest_model.pkl'")
