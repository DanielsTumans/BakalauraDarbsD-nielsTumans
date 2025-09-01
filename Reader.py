import os
import joblib
from collections import Counter

def safe_print(text=""):
    try:
        print(text.encode("cp1251", errors="ignore").decode("cp1251"))
    except:
        print(text)

svm_model = joblib.load("svm_model.pkl")
nb_model = joblib.load("naive_bayes_model.pkl")
rf_model = joblib.load("random_forest_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

articles_dir = "Articles"
files = sorted([f for f in os.listdir(articles_dir) if f.endswith(".txt")])

safe_print(f"\nFounded files: {len(files)}\n")

for i, fname in enumerate(files, 1):
    path = os.path.join(articles_dir, fname)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    title_line = next((line for line in lines if "Article:" in line), None)
    if not title_line:
        safe_print(f"Article not founded {fname}")
        continue

    title = title_line.split(":", 1)[1].strip()
    if not title:
        safe_print(f"Empty article in file {fname}")
        continue

    vec = vectorizer.transform([title])
    pred_svm = svm_model.predict(vec)[0]
    pred_nb = nb_model.predict(vec)[0]
    pred_rf = rf_model.predict(vec)[0]

    safe_print(f"File: {fname}")
    safe_print(f"Article: {title}")
    safe_print(f"SVM: {pred_svm}")
    safe_print(f"Naive Bayes: {pred_nb}")
    safe_print(f"Random Forest: {pred_rf}")
    safe_print("-" * 60)

    output_lines = []
    inserted = False
    for line in lines:
        output_lines.append(line)
        if "Date:" in line and not inserted:
            output_lines.append(f"SVM: {pred_svm}")
            output_lines.append(f"Naive Bayes: {pred_nb}")
            output_lines.append(f"Random Forest: {pred_rf}")
            inserted = True

    with open(path, "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")
