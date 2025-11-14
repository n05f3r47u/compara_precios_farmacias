import requests
from bs4 import BeautifulSoup
import re

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
# FARMATODO
# ----------------------------------------
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos&filtros="
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("div.card-ftd__card-unique")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("p.text-title")
            price = c.select_one("span.price__text-price")
            link = c.select_one("a.content-product")
            img = c.select_one("img.product-image__image")

            results.append({
                "store": "farmatodo",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": normalize_price(price.get_text(strip=True)) if price else None,
                "link": link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ----------------------------------------
# REBAJA
# ----------------------------------------
def scrape_rebaja(query, max_results=10):
    url = f"https://www.larebajavirtual.com/search?query={query}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("section.vtex-product-summary-2-x-container")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one(".vtex-product-summary-2-x-productNameContainer")
            price = c.select_one(".vtex-product-price-1-x-sellingPrice")
            link = c.select_one("a.vtex-product-summary-2-x-clearLink")
            img = c.select_one(".vtex-product-summary-2-x-imageNormal")

            results.append({
                "store": "rebaja",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": normalize_price(price.get_text(strip=True)) if price else None,
                "link": link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ----------------------------------------
# CRUZ VERDE
# ----------------------------------------
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("ml-card-product, div.product-item")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("a.font-open.flex.items-center")
            price = c.select_one("span.font-bold.text-prices")
            link = c.select_one("a.font-open.flex.items-center")
            img = c.select_one("img")

            results.append({
                "store": "cruzverde",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": normalize_price(price.get_text(strip=True)) if price else None,
                "link": link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ----------------------------------------
# PASTEUR
# ----------------------------------------
def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
    r = requests.get(url, headers=HEADERS, timeout=15)
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
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": normalize_price(price.get_text(strip=True)) if price else None,
                "link": link["href"] if link else None,
                "img": img["src"] if img else None
            })
        except:
            continue

    return results


# ----------------------------------------
# EXITO
# ----------------------------------------
def scrape_exito(query, max_results=10):
    url = f"https://www.exito.com/s?q={query}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("article[class*='productCard']")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("h3")
            price = c.select_one("p")
            link = c.select_one("a")
            img = c.select_one("img")

            results.append({
                "store": "exito",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
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
