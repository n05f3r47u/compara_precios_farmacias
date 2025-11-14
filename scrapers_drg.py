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
    url = "https://www.exito.com/api/catalog_system/pub/products/search/?ft=" + query
    r = requests.get(url, headers=HEADERS)
    items = r.json()

    results = []
    for p in items[:max_results]:
        try:
            price = p["items"][0]["sellers"][0]["commertialOffer"]["Price"]
            img = p["items"][0]["images"][0]["imageUrl"]
            link = p["link"]

            results.append({
                "store": "exito",
                "title": p["productName"],
                "price_raw": f"${price:,.0f}",
                "price": float(price),
                "link": link,
                "img": img
            })
        except:
            continue

    return results


# ----------------------------------------
# REBAJA (VTEX API)
# ----------------------------------------
def scrape_rebaja(query, max_results=10):
    url = "https://www.larebajavirtual.com/api/catalog_system/pub/products/search/?ft=" + query
    r = requests.get(url, headers=HEADERS)
    items = r.json()

    results = []
    for p in items[:max_results]:
        try:
            price = p["items"][0]["sellers"][0]["commertialOffer"]["Price"]
            img = p["items"][0]["images"][0]["imageUrl"]
            link = p["link"]

            results.append({
                "store": "rebaja",
                "title": p["productName"],
                "price_raw": f"${price:,.0f}",
                "price": float(price),
                "link": link,
                "img": img
            })
        except:
            continue
    return results


# ----------------------------------------
# PASTEUR (VTEX HTML)
# ----------------------------------------
def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("span.vtex-product-summary-2-x-productBrand")
            price = c.select_one("span.vtex-product-price-1-x-currencyContainer")
            link = c.select_one("a.vtex-product-summary-2-x-clearLink")
            img = c.select_one("img.vtex-product-summary-2-x-image")

            results.append({
                "store": "pasteur",
                "title": title.get_text(strip=True),
                "price_raw": price.get_text(strip=True),
                "price": normalize_price(price.get_text(strip=True)),
                "link": "https://www.farmaciaspasteur.com.co" + link["href"],
                "img": img["src"]
            })
        except:
            continue
    return results


# ----------------------------------------
# CRUZ VERDE (HTML directo)
# ----------------------------------------
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("div.product-card, ml-card-product")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("h3, h2, a")
            price = c.select_one(".prices, .price, span.font-bold")
            link = c.select_one("a")
            img = c.select_one("img")

            if not title: continue

            results.append({
                "store": "cruzverde",
                "title": title.get_text(strip=True),
                "price_raw": price.get_text(strip=True) if price else "",
                "price": normalize_price(price.get_text(strip=True)) if price else None,
                "link": link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ----------------------------------------
# MASTER SCRAPER
# ----------------------------------------
def scrape_all(query, max_results=6):
    return {
        "farmatodo": scrape_farmatodo(query, max_results),
        "pasteur": scrape_pasteur(query, max_results),
        "cruzverde": scrape_cruzverde(query, max_results),
        "rebaja": scrape_rebaja(query, max_results),
        "exito": scrape_exito(query, max_results),
    }
