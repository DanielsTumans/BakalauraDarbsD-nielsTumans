import sys
import re
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("window-size=1920x1080")

driver = webdriver.Chrome(options=options)

url = sys.argv[1]
driver.get(url)

all_articles = []
MAX_PAGES = 2

def wait_for_full_load(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def scroll_to_bottom(driver, pause_time=1.5, max_scrolls=4):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def detect_articles(soup):
    articles = soup.find_all("article")
    if articles:
        return articles
    candidates = []
    for block in soup.find_all(["div", "section", "li"]):
        if block.find("a", href=True) and block.find(["h1", "h2", "h3", "h4"]):
            candidates.append(block)
    return candidates

def extract_article_data(article, base_url):
    title_tag = article.find(["h1", "h2", "h3", "h4"])
    title = title_tag.get_text(strip=True) if title_tag else "No title"
    link_tag = article.find("a", href=True)
    link = urljoin(base_url, link_tag["href"]) if link_tag else "No link"
    img_tag = article.find("img", src=True)
    img = urljoin(base_url, img_tag["src"]) if img_tag else "No image"
    return title, link, img

def pick_href(els):
    for el in els:
        href = el.get_attribute("href")
        if href and href.strip():
            return href.strip()
    return None

def compute_next_url_fallback(current_url, page_num):
    m = re.search(r'([?&])page=(\d+)', current_url)
    if m:
        sep, n = m.group(1), int(m.group(2))
        return re.sub(r'([?&])page=\d+', f'{sep}page={n+1}', current_url)
    m = re.search(r'/page/(\d+)/?$', current_url)
    if m:
        n = int(m.group(1))
        return re.sub(r'/page/\d+/?$', f'/page/{n+1}/', current_url)
    return (current_url + ('&' if '?' in current_url else '?') + 'page=2') if 'page=' not in current_url else current_url

def go_next_page(driver, page_num):
    old_url = driver.current_url
    try:
        href = pick_href(driver.find_elements(By.CSS_SELECTOR, 'link[rel="next"]'))
        if href:
            driver.get(href); wait_for_full_load(driver); return driver.current_url != old_url
    except Exception:
        pass
    try:
        href = pick_href(driver.find_elements(By.CSS_SELECTOR, 'a[rel="next"]'))
        if href:
            driver.get(href); wait_for_full_load(driver); return driver.current_url != old_url
    except Exception:
        pass
    try:
        candidates = driver.find_elements(
            By.XPATH,
            '//a[contains(translate(normalize-space(.),"NEXTСЛЕДУЮЩАЯNĀKAMĀ","nextследующаяnākamā"),"next") or '
            'contains(normalize-space(.),"Next") or contains(normalize-space(.),"Nākamā")]'
        )
        href = pick_href(candidates)
        if href:
            driver.get(href); wait_for_full_load(driver); return driver.current_url != old_url
    except Exception:
        pass
    try:
        num = str(page_num + 1)
        number_links = driver.find_elements(By.XPATH, f'//a[normalize-space(text())="{num}"]')
        href = pick_href(number_links)
        if href:
            driver.get(href); wait_for_full_load(driver); return driver.current_url != old_url
    except Exception:
        pass
    try:
        href = compute_next_url_fallback(old_url, page_num)
        if href and href != old_url:
            driver.get(href); wait_for_full_load(driver); return driver.current_url != old_url
    except Exception:
        pass
    return False

for page_num in range(1, MAX_PAGES + 1):
    print(f"Loading page {page_num}...")
    try:
        wait_for_full_load(driver, timeout=15)
    except TimeoutException:
        print("Timeout, continuing anyway.")
    scroll_to_bottom(driver, pause_time=1.2, max_scrolls=5)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    page_url = driver.current_url
    articles = detect_articles(soup)
    all_articles.extend([(article, page_url) for article in articles])
    if not go_next_page(driver, page_num):
        print("Next page not found.")
        break

driver.quit()

with open("news_cards.txt", "w", encoding="utf-8") as f:
    print(f"Found articles: {len(all_articles)}")
    for i, (article, base_url) in enumerate(all_articles, 1):
        title, link, img = extract_article_data(article, base_url)
        f.write(f"Article №{i}\n")
        f.write(f"{title}\n")
        f.write(f"Link: {link}\n")
        f.write(f"Image: {img}\n\n")

print("All articles saved in 'news_cards.txt'")
