import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re
import time
import os


# ----------------------------------------------------
# CONFIGURACIÓN GLOBAL
# ----------------------------------------------------

# Headers para evitar bloqueos por parte de las tiendas
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
}

ENABLE_LOGS = True   # cambiar a True solo si quieres logs en _logs/
# Habilita logs HTML si necesitas depuración


# ----------------------------------------------------
# UTILIDAD: obtener BeautifulSoup con reintentos
# ----------------------------------------------------
def _get_soup(url, params=None, retries=2, timeout=10, log_prefix=None):
    """
    GET con headers, manejo de errores y logs opcionales.
    Retorna BeautifulSoup o None.
    """

    for attempt in range(retries + 1):
        try:
            r = requests.get(
                url,
                params=params,
                headers=DEFAULT_HEADERS,
                timeout=timeout,
            )

            # Guardar log del HTML si está habilitado
            if ENABLE_LOGS and log_prefix:
                os.makedirs("_logs", exist_ok=True)
                with open(f"_logs/{log_prefix}_attempt{attempt}.html", "w", encoding="utf-8") as f:
                    f.write(r.text[:20000])

            # Respuesta válida
            if r.status_code == 200 and r.text.strip():
                return BeautifulSoup(r.text, "html.parser")

        except Exception:
            pass

        time.sleep(0.5 * (attempt + 1))

    return None


# ----------------------------------------------------
# UTILIDAD: Normalización del precio
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


# ====================================================
# SCRAPERS (5 FARMACIAS)
# ====================================================

# ----------------------------------------------------
# 1. FARMATODO
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
            title_el = c.select_one("p.text-title")
            price_el = c.select_one("span.price__text-price")
            link_el = c.select_one("a[href]")
            img_el = c.select_one("img")

            link = (
                urljoin("https://www.farmatodo.com.co", link_el["href"])
                if link_el else None
            )
            img = img_el.get("src") if img_el else None

            results.append({
                "store": "Farmatodo",
                "title": title_el.get_text(strip=True) if title_el else None,
                "price_raw": price_el.get_text(strip=True) if price_el else None,
                "price": _normalize_price(price_el.get_text()) if price_el else None,
                "link": link,
                "img": img
            })
        except:
            continue

    return results


# ----------------------------------------------------
# 2. LA REBAJA
# ----------------------------------------------------
def scrape_rebaja(query, max_results=10):
    soup = _get_soup(
        "https://www.larebajavirtual.com/search",
        params={"query": query},
        log_prefix="rebaja"
    )

    if not soup:
        return []

    cards = soup.select("section.vtex-product-summary-2-x-container")
    results = []

    for c in cards[:max_results]:
        try:
            title_el = c.select_one(".vtex-product-summary-2-x-productNameContainer")
            price_el = (
                c.select_one(".vtex-product-price-1-x-sellingPriceValue")
                or c.select_one(".vtex-product-price-1-x-sellingPrice")
            )
            link_el = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
            img_el = c.select_one(".vtex-product-summary-2-x-imageNormal")

            link = link_el["href"] if link_el else None
            img = img_el.get("src") if img_el else None

            results.append({
                "store": "Rebaja",
                "title": title_el.get_text(strip=True) if title_el else None,
                "price_raw": price_el.get_text(strip=True) if price_el else None,
                "price": _normalize_price(price_el.get_text()) if price_el else None,
                "link": link,
                "img": img
            })
        except:
            continue

    return results


# ----------------------------------------------------
# 3. CRUZ VERDE
# ----------------------------------------------------
def scrape_cruzverde(query, max_results=10):
    base = "https://www.cruzverde.com.co"

    url = (
        f"{base}/search?query={query}"
    )

    soup = _get_soup(url, log_prefix="cruzverde")
    if not soup:
        return []

    cards = soup.select("ml-card-product")
    print({url})
    if not cards:
        cards = soup.select("article, div")

    results = []

    for c in cards[:max_results]:
        try:
            title_el = c.select_one("a.font-open.flex.items-center")
            price_el = c.select_one("span.font-bold.tex-.prices")
            link_el = c.select_one("a.font-open.flex.items-center[href]")
            img_el = c.select_one("img.ng-tns-c36-165") or c.select_one("img")

            # procesar link
            href = None
            if link_el:
                raw = link_el.get("href")
                href = urljoin(base, raw) if raw.startswith("/") else raw

            img = img_el.get("src") if img_el else None

            results.append({
                "store": "Cruzverde",
                "title": title_el.get_text(strip=True) if title_el else None,
                "price_raw": price_el.get_text(strip=True) if price_el else None,
                "price": _normalize_price(price_el.get_text()) if price_el else None,
                "link": href,
                "img": img
            })
        except:
            continue

    return results





# ----------------------------------------------------
# 4. PASTEUR (FIX: query multi-palabra)
# ----------------------------------------------------
def scrape_pasteur(query, max_results=10):
    base = "https://www.farmaciaspasteur.com.co"

    # Separar solo la primera palabra para el PATH
    parts = query.split()
    first = quote(parts[0])  # primera palabra codificada
    full_q = query.strip()

    url = f"{base}/{first}?_q={full_q}&map=ft"

    soup = _get_soup(url, log_prefix="pasteur")

    if not soup:
        return []

    cards = soup.select("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")
    if not cards:
        cards = soup.select("article, div")

    results = []

    for c in cards[:max_results]:
        try:
            title_el = c.select_one("span.vtex-product-summary-2-x-productBrand")
            price_el = (
                c.select_one("span.vtex-product-price-1-x-currencyInteger")
                or c.select_one("span.vtex-product-price-1-x-currencyContainer")
            )
            link_el = c.select_one("a.vtex-product-summary-2-x-clearLink[href]")
            img_el = c.select_one("img.vtex-product-summary-2-x-image") or c.select_one("img")

            # procesar link
            href = None
            if link_el:
                raw = link_el.get("href")
                href = urljoin(base, raw) if raw.startswith("/") else raw

            img = img_el.get("src") if img_el else None

            results.append({
                "store": "Pasteur",
                "title": title_el.get_text(strip=True) if title_el else None,
                "price_raw": price_el.get_text(strip=True) if price_el else None,
                "price": _normalize_price(price_el.get_text()) if price_el else None,
                "link": href,
                "img": img
            })
        except:
            continue

    return results



# ----------------------------------------------------
# 5. ÉXITO (HTML confirmado)
# ----------------------------------------------------
def scrape_exito(query, max_results=10):
    base = "https://www.exito.com"

    soup = _get_soup(
        f"{base}/s",
        params={"q": query},
        log_prefix="exito"
    )

    if not soup:
        return []

    cards = soup.select("article[class*=productCard_productCard]")
    results = []

    for c in cards[:max_results]:
        try:
            title_el = (
                c.select_one("h3.styles_name__qQJiK")
                or c.select_one("h3")
                or c.select_one("h2")
            )
            price_el = (
                c.select_one("p[data-fs-container-price-otros]")
                or c.select_one("p[data-fs-price-final]")
                or c.select_one("p")
            )
            link_el = c.select_one("a[data-testid=product-link]") or c.select_one("a[href]")
            img_el = c.select_one("a[data-testid=product-link] img") or c.select_one("img")

            # procesar link
            href = None
            if link_el:
                raw = link_el.get("href")
                href = raw if raw.startswith("http") else urljoin(base, raw)

            # procesar imagen
            img = None
            if img_el:
                img = img_el.get("src") or img_el.get("data-src")

            results.append({
                "store": "Exito",
                "title": title_el.get_text(strip=True) if title_el else None,
                "price_raw": price_el.get_text(strip=True) if price_el else None,
                "price": _normalize_price(price_el.get_text()) if price_el else None,
                "link": href,
                "img": img
            })

        except:
            continue

    return results


# ====================================================
# EJECUTAR TODAS LAS TIENDAS
# ====================================================
#def scrape_all(query, max_per_store=6, selected_stores=None):
def scrape_all(query, max_per_store=6):
    stores = {
        "Farmatodo": scrape_farmatodo,
        #"Pasteur": scrape_pasteur,
        "Cruz Verde": scrape_cruzverde,
        "Rebaja": scrape_rebaja,
        "Exito": scrape_exito
    }

    # Filtrar tiendas seleccionadas
    #if selected_stores:
    #    stores = {k: fn for k, fn in stores.items() if k in selected_stores}

    out = {}

    for name, fn in stores.items():
        try:
            out[name] = fn(query, max_results=max_per_store)
        except Exception as e:
            out[name] = []
            print(f"[ERROR en {name}] {e}")

    return out
if st.checkbox("Mostrar depuración"):
    st.subheader("Datos crudos devueltos por scrape_all()")
    st.json(data)
