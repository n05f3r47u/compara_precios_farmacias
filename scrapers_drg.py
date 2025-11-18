# scrapers_drg.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


# ----------------------------------------------------
# Normalizar precios
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
# FARMATODO
# ----------------------------------------------------
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = (soup.select("div.card-ftd__card-unique")
             or soup.select("article, div[class*=product]"))

    results = []
    for c in cards[:max_results]:
        title = c.select_one("p.text-title")
        price = c.select_one("span.price__text-price")
        link = c.select_one("a[href]")
        img = c.select_one("img")

        results.append({
            "store": "Farmatodo",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": urljoin("https://www.farmatodo.com.co", link["href"]) if link else None,
            "img": img["src"] if img else None
        })
    return results


# ----------------------------------------------------
# REBAJA (VTEX)
# ----------------------------------------------------
def scrape_rebaja(query, max_results=10):
    url = f"https://www.larebajavirtual.com/search?query={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("section.vtex-product-summary-2-x-container")
    results = []

    for c in cards[:max_results]:
        title = c.select_one(".vtex-product-summary-2-x-productNameContainer")
        price = (c.select_one(".vtex-product-price-1-x-sellingPriceValue")
                 or c.select_one(".vtex-product-price-1-x-sellingPrice"))
        link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
        img = c.select_one(".vtex-product-summary-2-x-imageNormal")

        results.append({
            "store": "Rebaja",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img else None
        })

    return results


# ----------------------------------------------------
# CRUZ VERDE
# ----------------------------------------------------
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = (soup.select("article.product-card")
             or soup.select("ml-card-product")
             or soup.select("article, div"))

    results = []
    for c in cards[:max_results]:
        title = (c.select_one(".product-name")
                 or c.select_one("h3")
                 or c.select_one("a.font-open"))
        price = c.select_one("span.product-price") or c.select_one("span.font-bold")
        link = c.select_one("a[href]")
        img = c.select_one("img")

        results.append({
            "store": "Cruz Verde",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img else None
        })

    return results


# ----------------------------------------------------
# PASTEUR (VTEX)
# ----------------------------------------------------
def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")
    results = []

    for c in cards[:max_results]:
        title = c.select_one("span.vtex-product-summary-2-x-productBrand")
        price = (c.select_one("span.vtex-product-price-1-x-currencyInteger")
                 or c.select_one("span.vtex-product-price-1-x-currencyContainer"))
        link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
        img = c.select_one("img.vtex-product-summary-2-x-image")

        results.append({
            "store": "Pasteur",
            "title": title.get_text(strip=True) if title else None,
            "price_raw": price.get_text(strip=True) if price else None,
            "price": _normalize_price(price.get_text()) if price else None,
            "link": link["href"] if link else None,
            "img": img["src"] if img else None
        })

    return results


# ----------------------------------------------------
# ÉXITO (React)
# ----------------------------------------------------
def scrape_exito(query, max_results=10):
    url = f"https://www.exito.com/s?q={query}"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("article[class*=productCard_productCard]")
    results = []

    for c in cards[:max_results]:

        # TÍTULO
        title_el = c.select_one("h3.styles_name__qQJiK") \
                    or c.select_one("h3") \
                    or c.select_one("h2")

        # PRECIO
        price_el = c.select_one("p[data-fs-container-price-otros=true]") \
                    or c.select_one("p[data-fs-price-final]") \
                    or c.select_one("p")

        # LINK
        link_el = c.select("a[data-testid=product-link]")
        link = None
        if link_el:
            link = link_el[0].get("href")
            if link and not link.startswith("http"):
                link = urljoin("https://www.exito.com", link)

        # IMAGEN
        img_el = c.select_one("a[data-testid=product-link] img")
        img = None
        if img_el:
            img = img_el.get("src") or img_el.get("data-src")

        results.append({
            "store": "Éxito",
            "title": title_el.get_text(strip=True) if title_el else None,
            "price_raw": price_el.get_text(strip=True) if price_el else None,
            "price": _normalize_price(price_el.get_text()) if price_el else None,
            "link": link,
            "img": img
        })

    return results



# ----------------------------------------------------
# Ejecutar todo
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
            out[name] = fn(query, max_results=max_per_store)
        except:
            out[name] = []
    return out
