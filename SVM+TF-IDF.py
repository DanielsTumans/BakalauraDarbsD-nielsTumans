import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
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

model = LinearSVC()
model.fit(X_train_vec, y_train)


y_pred = model.predict(X_test_vec)
print(classification_report(y_test, y_pred))

joblib.dump(model, "svm_model.pkl")

while True:
    new_input = input("\nInsert article ('stop' for closing): ").strip()
    if new_input.lower() == 'stop':
        break
    vec = vectorizer.transform([new_input])
    prediction = model.predict(vec)[0]
    print(f"Class: {prediction}")
