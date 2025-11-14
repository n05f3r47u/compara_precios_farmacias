import requests
from bs4 import BeautifulSoup
import re
import json

# ------------------------------------
#  HEADERS GENERALES
# ------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ------------------------------------
#  UTILIDAD DE NORMALIZACIÓN
# ------------------------------------
def normalize_price(txt):
    if not txt:
        return None
    t = re.sub(r"[^\d,\.]", "", txt)
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return None


# ================================================================
# FARMATODO — usa JSON interno en __NEXT_DATA__
# ================================================================
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/search?q={query}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return []

    soup = BeautifulSoup(r.text, "lxml")

    # obtener JSON de Next.js
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if not script:
        return []

    try:
        data = json.loads(script.text)
        products = data["props"]["pageProps"]["products"]["products"]
    except:
        return []

    results = []
    for p in products[:max_results]:
        try:
            results.append({
                "store": "farmatodo",
                "title": p.get("name"),
                "price_raw": p["price"]["formattedValue"],
                "price": normalize_price(p["price"]["formattedValue"]),
                "link": "https://www.farmatodo.com.co" + p.get("url", ""),
                "img": p.get("image")
            })
        except:
            continue

    return results


# ================================================================
# EXITO — API VTEX JSON (a veces devuelve HTML ? validación obligatoria)
# ================================================================
def scrape_exito(query, max_results=10):
    url = "https://www.exito.com/api/catalog_system/pub/products/search/?ft=" + query

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return []

    # validar que el response sea JSON
    try:
        items = r.json()
    except ValueError:  # respuesta HTML ? vacía
        return []

    if not isinstance(items, list):
        return []

    results = []
    for p in items[:max_results]:
        try:
            seller = p["items"][0]["sellers"][0]["commertialOffer"]
            price = seller["Price"]
            img = p["items"][0]["images"][0]["imageUrl"]
            link = p.get("link")

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


# ================================================================
# REBAJA — API VTEX JSON (misma validación que Exito)
# ================================================================
def scrape_rebaja(query, max_results=10):
    url = "https://www.larebajavirtual.com/api/catalog_system/pub/products/search/?ft=" + query

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return []

    # validar JSON
    try:
        items = r.json()
    except ValueError:
        return []

    if not isinstance(items, list):
        return []

    results = []
    for p in items[:max_results]:
        try:
            seller = p["items"][0]["sellers"][0]["commertialOffer"]
            price = seller["Price"]
            img = p["items"][0]["images"][0]["imageUrl"]
            link = p.get("link")

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


# ================================================================
# PASTEUR — HTML VTEX (requests + BeautifulSoup)
# ================================================================
def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return []

    soup = BeautifulSoup(r.text, "lxml")
    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")

    results = []
    for c in cards[:max_results]:
        try:
            title = c.select_one("span.vtex-product-summary-2-x-productBrand")
            price = c.select_one("span.vtex-product-price-1-x-currencyContainer")
            link = c.select_one("a.vtex-product-summary-2-x-clearLink")
            img = c.select_one("img.vtex-product-summary-2-x-image")

            if not (title and price):
                continue

            results.append({
                "store": "pasteur",
                "title": title.get_text(strip=True),
                "price_raw": price.get_text(strip=True),
                "price": normalize_price(price.get_text(strip=True)),
                "link": "https://www.farmaciaspasteur.com.co" + link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ================================================================
# CRUZ VERDE — HTML directo (pero validado)
# ================================================================
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except:
        return []

    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("div.product-card, ml-card-product, div.product-item")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("h3") or c.select_one("h2") or c.select_one("a")
            price = c.select_one(".prices, .pric_
