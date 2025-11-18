# scrapers_drg.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


# ----------------------------------------------------
# Utilidad: normalizar precios
# ----------------------------------------------------
def _normalize_price(text):
    if not text:
        return None
    t = re.sub(r"[^\d,\.]", "", text)
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return None


# ----------------------------------------------------
# SCRAPER: FARMATODO
# ----------------------------------------------------
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    cards = soup.select("div.card-ftd__card-unique") or soup.select("article, div[class*=product]")

    for c in cards[:max_results]:
        title = c.select_one("p.text-title")
        price = c.select_one("span.price__text-price")
        link = c.select_one("a[href]")
        img = c.select_one("img")

        item = {
            "store": "Farmatodo",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": urljoin("https://www.farmatodo.com.co", link["href"]) if link else None,
            "img": img["src"] if img and img.get("src") else None
        }
        results.append(item)

    return results


# ----------------------------------------------------
# SCRAPER: REBAJA
# ----------------------------------------------------
def scrape_rebaja(query, max_results=10):
    url = f"https://www.larebajavirtual.com/search?query={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    cards = soup.select("section.vtex-product-summary-2-x-container")

    for c in cards[:max_results]:
        title = c.select_one(".vtex-product-summary-2-x-productNameContainer")
        price = c.select_one(".vtex-product-price-1-x-sellingPrice")
        link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
        img = c.select_one(".vtex-product-summary-2-x-imageNormal")

        item = {
            "store": "Rebaja",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img and img.get("src") else None
        }
        results.append(item)

    return results


# ----------------------------------------------------
# SCRAPER: CRUZ VERDE
# ----------------------------------------------------
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    cards = soup.select("ml-card-product") or soup.select("article, div")

    for c in cards[:max_results]:
        title = c.select_one("a.font-open")
        price = c.select_one("span.font-bold")
        link = c.select_one("a[href]")
        img = c.select_one("img")

        item = {
            "store": "Cruz Verde",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img else None
        }
        results.append(item)

    return results


# ----------------------------------------------------
# SCRAPER: PASTEUR
# ----------------------------------------------------
def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")

    for c in cards[:max_results]:
        title = c.select_one("span.vtex-product-summary-2-x-productBrand")
        price = c.select_one("span.vtex-product-price-1-x-currencyContainer")
        link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
        img = c.select_one("img")

        item = {
            "store": "Pasteur",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img else None
        }
        results.append(item)

    return results


# ----------------------------------------------------
# SCRAPER: ÉXITO
# ----------------------------------------------------
def scrape_exito(query, max_results=10):
    url = f"https://www.exito.com/s?q={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    cards = soup.select("article[class*=productCard]")

    for c in cards[:max_results]:
        title = c.select_one("h3") or c.select_one("h2")
        price = c.select_one("p")
        link = c.select_one("a[href]")
        img = c.select_one("img")

        item = {
            "store": "Exito",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": urljoin("https://www.exito.com", link["href"]) if link else None,
            "img": img["src"] if img else None
        }
        results.append(item)

    return results


# ----------------------------------------------------
# Ejecutar todos los scrapers
# ----------------------------------------------------
def scrape_all(query, max_per_store=6, selected_stores=None):
    stores = {
        "Farmatodo": scrape_farmatodo,
        "Pasteur": scrape_pasteur,
        "Cruz Verde": scrape_cruzverde,
        "Rebaja": scrape_rebaja,
        "Exito": scrape_exito
    }

    if selected_stores:
        stores = {k: v for k, v in stores.items() if k in selected_stores}

    out = {}
    for name, fn in stores.items():
        try:
            out[name] = fn(query, max_per_store)
        except:
            out[name] = []

    return out
