import os
import sys
import requests
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(errors="replace")
    sys.stderr.reconfigure(errors="replace")
except Exception:
    pass

os.makedirs("Articles", exist_ok=True)

with open("news_cards.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

links = []
for line in lines:
    if "Link:" in line:
        url = line.split("Link:")[-1].strip()
        if url:
            links.append(url)
print(f"Founded: {len(links)}")

seen_links = set()
existing_titles = set()
article_count = 0

for i, url in enumerate(links, 1):
    if not url or url in seen_links:
        continue
    seen_links.add(url)

    print(f"\nProcess #{i}: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("h1") or soup.find("h2") or soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else f"Article {i}"
        if title in existing_titles:
            print("Duplicate title. Skip.")
            continue
        existing_titles.add(title)

        date = ""
        time_tag = soup.find("time")
        if time_tag:
            date = time_tag.get_text(strip=True)
        else:
            meta_date = (
                soup.find("meta", {"property": "article:published_time"})
                or soup.find("meta", {"name": "date"})
                or soup.find("meta", {"name": "pubdate"})
            )
            if meta_date and meta_date.get("content"):
                date = meta_date["content"]
            else:
                span_date = soup.find("span", class_="date") or soup.find("div", class_="date")
                if span_date:
                    date = span_date.get_text(strip=True)

        paragraphs = []

        article_block = soup.find("article")
        if article_block:
            for p in article_block.find_all("p"):
                text = p.get_text(strip=True)
                if text and len(text) > 15:
                    paragraphs.append(text)

        if len(paragraphs) < 3:
            for container in soup.find_all(["section", "div"], recursive=True):
                if container.find("p"):
                    for p in container.find_all("p"):
                        text = p.get_text(strip=True)
                        if text and len(text) > 15:
                            paragraphs.append(text)
                    if len(paragraphs) >= 5:
                        break

        seen_lines = set()
        cleaned = []
        stop_phrases = ["abonēšanas", "subscribe", "cookies"]
        bad_words = ["instagram", "facebook", "youtube", "twitter", "telegram"]

        for line in paragraphs:
            low = line.lower()
            if any(stop in low for stop in stop_phrases):
                continue
            if any(bad in low for bad in bad_words):
                continue
            if line not in seen_lines:
                seen_lines.add(line)
                cleaned.append(line)

        if not cleaned:
            print("No article text. Skip.")
            continue

        article_count += 1
        output_path = os.path.join("Articles", f"article_{article_count}.txt")
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(f"Article: {title}\n")
            f_out.write(f"Date: {date}\n\n")
            f_out.write("Text:\n")
            f_out.write("\n".join(cleaned))

        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
