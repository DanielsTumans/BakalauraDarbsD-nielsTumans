import os
import sys
import joblib
from sklearn.cluster import KMeans

sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 2:
    print("Insert doc name.")
    sys.exit()

target_filename = sys.argv[1]

articles_dir = "Articles"
documents, titles, filenames = [], [], []

for fname in sorted(os.listdir(articles_dir)):
    if fname.endswith(".txt"):
        path = os.path.join(articles_dir, fname)
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        title_line = next((l for l in lines if l.startswith("Article:")), None)
        title = title_line.split(":", 1)[1].strip() if title_line and ":" in title_line else "None"
        start = next((i for i, l in enumerate(lines) if "Text:" in l), None)
        content = " ".join(lines[start + 1:]) if start is not None else ""
        if content:
            documents.append(content)
            titles.append(title)
            filenames.append(fname)

if target_filename not in filenames:
    print(f"File {target_filename} not found.")
    sys.exit()

vectorizer = joblib.load("tfidf_vectorizer.pkl")
X = vectorizer.transform(documents)
kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
labels = kmeans.fit_predict(X)

selected_index = filenames.index(target_filename)
selected_cluster = labels[selected_index]

out_path = "clusters_kmeans.txt"
unique_clusters = sorted(set(labels))
with open(out_path, "w", encoding="utf-8") as f:
    f.write("KMeans clusters mapping\n")
    f.write(f"Total files: {len(filenames)}\n")
    f.write(f"Total clusters: {len(unique_clusters)}\n\n")

    for cid in unique_clusters:
        f.write(f"Cluster {cid}:\n")
        for fname, title, lab in zip(filenames, titles, labels):
            if lab == cid:
                f.write(f"  {fname} — {title}\n")
        f.write("\n")

    f.write("Flat mapping (filename -> cluster):\n")
    for fname, lab in zip(filenames, labels):
        f.write(f"{fname}\t{lab}\n")

print(f"\nArticle: {filenames[selected_index]} — {titles[selected_index]}")
print("Other articles:")
for i, (fname, title, lab) in enumerate(zip(filenames, titles, labels)):
    if i != selected_index and lab == selected_cluster:
        print(f"- {fname} — {title}")

print(f"\nSaved full mapping to: {out_path}")
