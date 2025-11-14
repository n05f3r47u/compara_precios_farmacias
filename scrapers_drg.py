import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def normalize_price(txt):
    if not txt:
        return None
    t = re.sub(r"[^\d,\.]", "", txt)
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return None


# ----------------------------------------
# FARMATODO (usa JSON interno)
# ----------------------------------------
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/search?q={query}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "lxml")

    data_script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not data_script:
        return []

    data = json.loads(data_script.text)
    try:
        products = data["props"]["pageProps"]["products"]["products"]
    except:
        return []

    results = []
    for p in products[:max_results]:
        try:
            results.append({
                "store": "farmatodo",
                "title": p["name"],
                "price_raw": p["price"]["formattedValue"],
                "price": normalize_price(p["price"]["formattedValue"]),
                "link": "https://www.farmatodo.com.co" + p["url"],
                "img": p["image"]
            })
        except:
            continue
    return results


# ----------------------------------------
# EXITO (VTEX API)
# ----------------------------------------
def scrape_exito(query, max_results=10):
    url = "https://www.exito.com/a
