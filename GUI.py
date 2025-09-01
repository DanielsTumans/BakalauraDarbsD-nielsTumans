import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel
import subprocess
import threading

selected_url = "https://www.delfi.lv/archive/latest"

def run_script(script_name, button, status_message, success_message, callback=None):
    button.config(state="disabled")
    status_label.config(text=status_message)

    def task():
        try:
            args = ["python", script_name]
            if script_name == "main.py":
                args.append(selected_url)
            result = subprocess.run(args, capture_output=True, text=True)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, result.stdout)
            if result.stderr:
                output_text.insert(tk.END, "\nError:\n" + result.stderr)
            status_label.config(text=success_message)
            if callback:
                callback()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            button.config(state="normal")

    threading.Thread(target=task).start()

def run_main():
    global selected_url
    selected_url = url_entry.get().strip()
    if not selected_url:
        messagebox.showwarning("Attention", "Please insert Url")
        return
    run_script("main.py", btn_main, "Process...", "Links ready.")

def run_news():
    run_script("News.py", btn_news, "Process...", "Articles ready.", load_articles)

def run_reader():
    run_script("Reader.py", btn_reader, "Classification...", "Classifications ready.", load_articles)

def load_articles():
    listbox.delete(0, tk.END)
    articles_dir = "Articles"
    if not os.path.exists(articles_dir):
        return
    for fname in sorted(os.listdir(articles_dir)):
        if fname.endswith(".txt"):
            with open(os.path.join(articles_dir, fname), encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Article:"):
                        title = line.split(":", 1)[1].strip()
                        listbox.insert(tk.END, f"{fname} — {title}")
                        break

def show_article(event):
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    filename = listbox.get(index).split(" — ")[0]

    new_window = Toplevel(window)
    new_window.title(filename)
    new_window.geometry("800x600")

    text_area = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, font=("Arial", 11))
    text_area.pack(expand=True, fill=tk.BOTH)

    with open(os.path.join("Articles", filename), encoding="utf-8") as f:
        content = f.read()
        text_area.insert(tk.END, content)

    title_line = next((line for line in content.splitlines() if line.startswith("Заголовок:")), "")
    title = title_line.replace("Article:", "").strip()

    def save_to_dataset(class_name):
        path = os.path.join("Data_set_1", f"{class_name}.txt")
        try:
            with open(path, "a", encoding="utf-8") as f_out:
                f_out.write(title + "\n")
            messagebox.showinfo("Complete", f"Title ready in {class_name}.txt")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    class_frame = tk.Frame(new_window)
    class_frame.pack(pady=5)

    class_names = ["Auto", "Bizness", "Kultura", "Life", "Sports"]
    for idx, name in enumerate(class_names):
        btn = tk.Button(class_frame, text=name, font=("Arial", 10),
                        command=lambda n=name: save_to_dataset(n))
        btn.grid(row=0, column=idx, padx=5)

    btn_kmeans = tk.Button(new_window, text="Clustering KMeans",
                           command=lambda: run_clustering("Clusering_KMeans.py", filename))
    btn_kmeans.pack(pady=2)

    btn_dbscan = tk.Button(new_window, text="Clustering DBSCAN",
                           command=lambda: run_clustering("Clustering_DBSCAN.py", filename))
    btn_dbscan.pack(pady=2)

    btn_other = tk.Button(new_window, text="Clustering",
                          command=lambda: run_clustering("Clustering.py", filename))
    btn_other.pack(pady=2)



def run_clustering(script_name, filename):
    try:
        result = subprocess.run(["python", script_name, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace")
        output = result.stdout.strip() or "Nothing."
        if result.stderr:
            output += "\n\nErrors:\n" + result.stderr

        cluster_window = Toplevel(window)
        cluster_window.title(f"Clustering result: {script_name}")
        cluster_window.geometry("700x500")

        text_area = scrolledtext.ScrolledText(cluster_window, wrap=tk.WORD, font=("Arial", 11))
        text_area.pack(expand=True, fill=tk.BOTH)
        text_area.insert(tk.END, output)
        text_area.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_articles():
    articles_dir = "Articles"
    if not os.path.exists(articles_dir):
        messagebox.showinfo("Deleting", "Articles not found.")
        return

    deleted = 0
    for fname in os.listdir(articles_dir):
        if fname.endswith(".txt"):
            try:
                os.remove(os.path.join(articles_dir, fname))
                deleted += 1
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return

    load_articles()
    messagebox.showinfo("Deleting completed", f"Deleted files: {deleted}")
window = tk.Tk()
window.title("News analyse")
window.geometry("1000x850")

url_label = tk.Label(window, text="Insert link:", font=("Arial", 12))
url_label.pack(pady=5)

url_entry = tk.Entry(window, font=("Arial", 12))
url_entry.insert(0, selected_url)
url_entry.pack(fill=tk.X, padx=10, pady=5)

btn_main = tk.Button(window, text="(main.py)", command=run_main, font=("Arial", 12))
btn_main.pack(pady=5)

btn_news = tk.Button(window, text="(News.py)", command=run_news, font=("Arial", 12))
btn_news.pack(pady=5)

btn_reader = tk.Button(window, text="(Reader.py)", command=run_reader, font=("Arial", 12))
btn_reader.pack(pady=5)

btn_clear = tk.Button(window, text="Delete all articles", command=delete_articles, font=("Arial", 12))
btn_clear.pack(pady=5)

status_label = tk.Label(window, text="Ready.", font=("Arial", 12), fg="gray")
status_label.pack(pady=5)

output_text = tk.Text(window, height=10, wrap=tk.WORD, font=("Courier", 10))
output_text.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

listbox = tk.Listbox(window, font=("Arial", 11))
listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
listbox.bind("<<ListboxSelect>>", show_article)

window.mainloop()