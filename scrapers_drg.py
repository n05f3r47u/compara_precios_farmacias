# scrapers_drg.py (versión completa con logs y correcciones finales)

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import os


# ----------------------------------------------------
# Headers comunes para evitar bloqueos
# ----------------------------------------------------
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


# ----------------------------------------------------
# Función utilitaria con logs automáticos
# Guarda HTML parcial si el sitio no devuelve productos
# ----------------------------------------------------
def _get_soup(url, params=None, retries=2, timeout=10, log_prefix=None):
    """
    Ejecuta GET con headers, reintentos y logging si algo falla.
    Retorna BeautifulSoup o None.
    """
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=timeout)

            # Guardar respuesta parcial si hay problemas
            if log_prefix:
                os.makedirs("_logs", exist_ok=True)
                with open(f"_logs/{log_prefix}_attempt{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(r.text[:20000])

            if r.status_code == 200 and r.text:
                return BeautifulSoup(r.text, "html.parser")

            time.sleep(0.6 * (attempt + 1))

        except Exception as e:
            time.sleep(0.6 * (attempt + 1))

    return None


# ----------------------------------------------------
# Normalizar precio
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
# FARMATODO (estable)
# ----------------------------------------------------
def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos"

    soup = _get_soup(url, log_prefix="farmatodo")
    if not soup:
        return []

    cards = soup.select("div.card-ftd__card-unique")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("p.text-title")
            price = c.select_one("span.price__text-price")
            link = c.select_one("a[href]")
            img = c.select_one("img")

            results.append({
                "store": "Farmatodo",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": _normalize_price(price.get_text()) if price else None,
                "link": urljoin("https://www.farmatodo.com.co", link.get("href")) if link else None,
                "img": img.get("src") if img else None
            })
        except:
            continue

    return results


# ----------------------------------------------------
# REBAJA (VTEX estable)
# ----------------------------------------------------
def scrape_rebaja(query, max_results=10):
    url = f"https://www.larebajavirtual.com/search"

    soup = _get_soup(url, params={"query": query}, log_prefix="rebaja")
    if not soup:
        return []

    cards = soup.select("section.vtex-product-summary-2-x-container")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one(".vtex-product-summary-2-x-productNameContainer")
            price = c.select_one(".vtex-product-price-1-x-sellingPriceValue") or \
                    c.select_one(".vtex-product-price-1-x-sellingPrice")
            link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
            img = c.select_one(".vtex-product-summary-2-x-imageNormal")

            results.append({
                "store": "Rebaja",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": _normalize_price(price.get_text()) if price else None,
                "link": link.get("href") if link else None,
                "img": img.get("src") if img else None
            })
        except:
            continue

    return results


# ----------------------------------------------------
# CRUZ VERDE
# ----------------------------------------------------
def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search"

    soup = _get_soup(url, params={"query": query}, log_prefix="cruzverde")
    if not soup:
        return []

    cards = soup.select("article.product-card") or soup.select("ml-card-product")
    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("h3") or c.select_one(".product-name")
            price = c.select_one("span.product-price") or c.select_one("span.font-bold")
            link = c.select_one("a[href]")
            img = c.select_one("img")

            results.append({
                "store": "Cruz Verde",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": _normalize_price(price.get_text()) if price else None,
                "link": link.get("href") if link else None,
                "img": img.get("src") if img else None
            })
        except:
            continue

    return results


# ----------------------------------------------------
# PASTEUR — FIX multi-palabra y mejor endpoint VTEX
# ----------------------------------------------------
def scrape_pasteur(query, max_results=10):
    base = "https://www.farmaciaspasteur.com.co"

    soup = _get_soup(
        f"{base}/search",
        params={"_q": query, "map": "ft"},
        log_prefix="pasteur"
    )

    if not soup:
        return []

    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")
    if not cards:
        cards = soup.select("article, div")

    results = []
    for c in cards[:max_results]:
        try:
            title = c.select_one("span.vtex-product-summary-2-x-productBrand")
            price = c.select_one("span.vtex-product-price-1-x-currencyInteger") or \
                    c.select_one("span.vtex-product-price-1-x-currencyContainer")
            link = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
            img = c.select_one("img.vtex-product-summary-2-x-image")

            href = link.get("href") if link else None
            if href and href.startswith("/"):
                href = urljoin(base, href)

            img_src = img.get("src") if img else None

            results.append({
                "store": "Pasteur",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": _normalize_price(price.get_text()) if price else None,
                "link": href,
                "img": img_src
            })
        except:
            continue

    return results


# ----------------------------------------------------
# ÉXITO — Ajustado exactamente al HTML que enviaste
# ----------------------------------------------------
def scrape_exito(query, max_results=10):
    base = "https://www.exito.com"
    soup = _get_soup(f"{base}/s", params={"q": query}, log_prefix="exito")

    if not soup:
        return []

    cards = soup.select("article[class*=productCard_productCard]")
    if not cards:
        cards = soup.select("article")

    results = []

    for c in cards[:max_results]:
        try:
            title = c.select_one("h3.styles_name__qQJiK") or c.select_one("h3") or c.select_one("h2")
            price = c.select_one("p[data-fs-container-price-otros]") or \
                    c.select_one("p[data-fs-price-final]") or \
                    c.select_one("p")
            link = c.select_one("a[data-testid=product-link]") or c.select_one("a[href]")
            img = c.select_one("a[data-testid=product-link] img") or c.select_one("img")

            href = None
            if link:
                raw = link.get("href")
                href = raw if raw.startswith("http") else urljoin(base, raw)

            img_src = None
            if img:
                img_src = img.get("src") or img.get("data-src")

            results.append({
                "store": "Exito",
                "title": title.get_text(strip=True) if title else None,
                "price_raw": price.get_text(strip=True) if price else None,
                "price": _normalize_price(price.get_text()) if price else None,
                "link": href,
                "img": img_src
            })
        except:
            continue

    return results


# ----------------------------------------------------
# Ejecutar todas las tiendas
# ----------------------------------------------------
def scrape_all(query, max_per_store=6, selected_stores=None):

    stores = {
        "Farmatodo": scrape_farmatodo,
        "Pasteur": scrape_pasteur,
        "Cruz Verde": scrape_cruzverde,
        "Rebaja": scrape_rebaja,
        "Exito": scrape_exito
    }

    # Filtrar tiendas seleccionadas correctamente
    if selected_stores:
        stores = {k: fn for k, fn in stores.items() if k in selected_stores}

    out = {}

    for name, fn in stores.items():
        try:
            out[name] = fn(query, max_results=max_per_store)
        except Exception as e:
            out[name] = []
            print(f"[ERROR en {name}] {e}")

    return out
