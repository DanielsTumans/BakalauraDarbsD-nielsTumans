import os
import sys
from sklearn.cluster import DBSCAN
import joblib
sys.stdout.reconfigure(encoding='utf-8')
articles_dir = "Articles"

documents = []
titles = []
filenames = []

for fname in sorted(os.listdir(articles_dir)):
    if fname.endswith(".txt"):
        path = os.path.join(articles_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        title = next((line.replace("Article:", "").strip() for line in lines if line.startswith("Article:")), "")
        content_index = next((i for i, line in enumerate(lines) if "Text:" in line), None)
        if content_index is not None:
            content = " ".join(lines[content_index+1:])
            if content:
                documents.append(content)
                titles.append(title)
                filenames.append(fname)

if len(sys.argv) < 2:
    print("Write the file name")
    sys.exit()

filename = sys.argv[1]
if filename not in filenames:
    print(f"File {filename} not found.")
    sys.exit()

selected_index = filenames.index(filename)

vectorizer = joblib.load("tfidf_vectorizer.pkl")
X = vectorizer.fit_transform(documents)

dbscan = DBSCAN(eps=0.7, min_samples=2, metric='cosine')
labels = dbscan.fit_predict(X)

out_path = "clusters_dbscan.txt"
unique_clusters = sorted(c for c in set(labels) if c != -1)
noise_count = sum(1 for v in labels if v == -1)

with open(out_path, "w", encoding="utf-8") as f:
    f.write("DBSCAN clusters mapping\n")
    f.write(f"Total files: {len(filenames)}\n")
    f.write(f"Total clusters (excluding noise): {len(unique_clusters)}\n")
    f.write(f"Noise points (-1): {noise_count}\n\n")

    for cid in unique_clusters:
        f.write(f"Cluster {cid}:\n")
        for fname, title, lab in zip(filenames, titles, labels):
            if lab == cid:
                f.write(f"  {fname} — {title}\n")
        f.write("\n")

    if noise_count:
        f.write("Noise (-1):\n")
        for fname, title, lab in zip(filenames, titles, labels):
            if lab == -1:
                f.write(f"  {fname} — {title}\n")
        f.write("\n")

    f.write("Flat mapping (filename -> cluster):\n")
    for fname, lab in zip(filenames, labels):
        f.write(f"{fname}\t{lab}\n")

selected_label = labels[selected_index]
if selected_label == -1:
    print(f"\nArticle {filename} not included.")
else:
    same_cluster_indices = [i for i, lab in enumerate(labels) if lab == selected_label and i != selected_index]
    if not same_cluster_indices:
        print(f"\nArticles {filename} — only one article in cluster {selected_label}.")
    else:
        print(f"\nChoosed article: {filenames[selected_index]} — {titles[selected_index]}")
        print(f"Cluster: {selected_label}")
        print("\nOther articles:")
        for idx in same_cluster_indices:
            print(f"- {filenames[idx]} — {titles[idx]}")

print(f"\nSaved full mapping to: {out_path}")
