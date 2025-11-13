# scrapers_drg.py
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import re
import time
from urllib.parse import urljoin


DEFAULT_TIMEOUT = 10000  # ms

def _normalize_price(text):
    if not text:
        return None
    # quita caracteres no numéricos excepto coma y punto
    t = re.sub(r'[^\d,\.]', '', text).strip()
    # convertir formatos colombianos: "3.499" o "3.499,00"
    # strategy: eliminar puntos de miles, reemplazar coma decimal por punto
    if t.count(',') == 1 and t.count('.') >= 1:
        # formato como 3.499,00 -> quitar puntos y cambiar coma por punto
        t = t.replace('.', '').replace(',', '.')
    else:
        # formato 3.499 o 3499 -> quitar puntos
        t = t.replace('.', '')
    try:
        return float(t)
    except:
        return None

def _make_page(pw, headless=True):
    browser = pw.chromium.launch(
        headless=headless,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--single-process",
            "--no-zygote"
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.set_default_timeout(DEFAULT_TIMEOUT)
    return browser, page


FARMATODO_BASE = "https://www.farmatodo.com.co/"

def scrape_farmatodo(query, max_results=10, headless=True):
    """
    Scraper ajustado para exito usando selectores detectados en el HTML proporcionado.
    - Card selector: article[class*="productCard"]
    - Title: h3.styles_name__qQJiK
    - Link: a[data-testid="product-link"] -> href (relativo)
    - Image: a[data-testid="product-link"] img -> src
    - Price: p.ProductPrice_container__price__XmMWA
    """
    results = []
    with sync_playwright() as pw:
        browser, page = _make_page(pw, headless=headless)
        try:
            url = f"{FARMATODO_BASE}/buscar?product={query}&departamento=Todos&filtros="
            #print url
            page.goto(url)
            # esperar un poco para que cargue JS y productos
            page.wait_for_timeout(10000)

            # selector de tarjetas robusto (busca cualquier clase que contenga productCard)
            cards = page.query_selector_all('div.card-ftd__card-unique')
            if not cards:
                # fallback más amplio
                cards = page.query_selector_all('article, div[class*="product"], li[class*="product-item"]')

            for c in cards[:max_results]:
                try:
                    title_el = c.query_selector('p.text-title')
                    link_el = c.query_selector('a.content-product, a[href]')
                    img_el = c.query_selector('img.product-image__image')
                    price_el = c.query_selector('span.price__text-price')
                    title = title_el.inner_text().strip() if title_el else None
                    price_raw = price_el.inner_text().strip() if price_el else None

                    href = link_el.get_attribute('href') if link_el else None
                    # convertir link relativo a absoluto
                    if href and href.startswith('/'):
                        href = urljoin(FARMATODO_BASE, href)

                    img = img_el.get_attribute('src') if img_el else None
                    # algunas imágenes están en data-src u otros atributos; intentar extras
                    if img is None and img_el:
                        img = img_el.get_attribute('data-src') or img_el.get_attribute('data-lazy-src')

                    item = {
                        "store": "Farmatodo",
                      #  "url": url,
                        "title": title,
                        "price_raw": price_raw,
                        "price": _normalize_price(price_raw) if price_raw else None,
                        "link": href,
                        "img": img
                    }
                    results.append(item)
                except Exception:
                    # no detener todo si una tarjeta falla; seguir con la siguiente
                    continue
        except PWTimeout:
            pass
        finally:
            browser.close()
    return results
    

REBAJA_BASE = "https://www.larebajavirtual.com"

def scrape_rebaja(query, max_results=10, headless=True):
    """
    Scraper para Tiendas D1.
    Busca productos por nombre, extrae nombre, precio, imagen y enlace.
    """
    results = []
    
    with sync_playwright() as pw:
        browser, page = _make_page(pw, headless=headless)
        try:
            url = f"{REBAJA_BASE}/search?query={query}"
            page.goto(url)
            page.wait_for_timeout(10000)
            cards = page.query_selector_all('section.vtex-product-summary-2-x-container')
            for c in cards[:max_results]:
                try:
                    title_el = c.query_selector('.vtex-product-summary-2-x-productNameContainer')
                    price_el = c.query_selector('.vtex-product-price-1-x-sellingPrice')
                    link_el = c.query_selector('a.vtex-product-summary-2-x-clearLink[href]')
                    img_el = c.query_selector('.vtex-product-summary-2-x-imageNormal')
                    price_raw = price_el.inner_text().strip() if price_el else None
                    item = {
                        "store": "Rebaja",
                        "title": (title_el.inner_text().strip() if title_el else None),
                        "price_raw": price_raw,
                        "price": _normalize_price(price_raw) if price_raw else None,
                        "link": (link_el.get_attribute('href') if link_el else None),
                        "img": (img_el.get_attribute('src') if img_el else None)
                    }
                    results.append(item)
                except Exception:
                    continue
        except PWTimeout:
            pass
        finally:
            browser.close()
    return results

def scrape_cruzverde(query, max_results=10, headless=True):
    #"""
    #Ara selectors (best-effort):
    #- tarjetas: div.product, li.product-item, .product-card
    #- título: h3, h2, .product-title
    #- precio: .price, span.price
    #"""
    results = []
    with sync_playwright() as pw:
        browser, page = _make_page(pw, headless=headless)
        try:
            url = f"https://www.cruzverde.com.co/search?query={query}"
            page.goto(url)
            page.wait_for_timeout(10000)
            cards = page.query_selector_all('ml-card-product')
            for c in cards[:max_results]:
                try:
                    title_el = c.query_selector('a.font-open.flex.items-center')
                    price_el = c.query_selector('span.font-bold.text-prices')
                    link_el = c.query_selector('a.font-open.flex.items-center[href]')
                    img_el = c.query_selector('img.ng-tns-c36-165')
                    price_raw = price_el.inner_text().strip() if price_el else None
                    item = {
                        "store": "Cruz verde",
                        "title": (title_el.inner_text().strip() if title_el else None),
                        "price_raw": price_raw,
                        "price": _normalize_price(price_raw) if price_raw else None,
                        "link": (link_el.get_attribute('href') if link_el else None),
                        "img": (img_el.get_attribute('src') if img_el else None)
                    }
                    results.append(item)
                except Exception:
                    continue
        except PWTimeout:
            pass
        finally:
            browser.close()
    return results



def scrape_pasteur(query, max_results=10, headless=True):
    """
    Scraper para olimpica.com
    Extrae nombre, precio, imagen y enlace del producto
    """
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()
        try:
            url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
            page.goto(url)
            page.wait_for_timeout(10000)  # Esperar a que se cargue el contenido

            products = page.query_selector_all('div.vtex-flex-layout-0-x-flexCol--col-general-product-info')
            for p in products[:max_results]:
                try:
                    title_el = p.query_selector('span.vtex-product-summary-2-x-productBrand')
                    price_el = p.query_selector('span.vtex-product-price-1-x-currencyContainer')
                    link_el = p.query_selector('a.vtex-product-summary-2-x-clearLink[href]')
                    img_el = p.query_selector('img.vtex-product-summary-2-x-image')

                    title = title_el.inner_text().strip() if title_el else None
                    price_raw = price_el.inner_text().strip() if price_el else None
                    href = link_el.get_attribute('href') if link_el else None
                    href = urljoin(OLIMPICA_BASE, href) if href else None
                    img = img_el.get_attribute('src') if img_el else None

                    results.append({
                        "store": "Farmacias Pasteur",
                        "title": title,
                        "price_raw": price_raw,
                        "price": _normalize_price(price_raw),
                        "link": href,
                        "img": img
                    })
                except Exception:
                    continue
        except PWTimeout:
            pass
        finally:
            browser.close()

    return results

EXITO_BASE = "https://www.exito.com"

def scrape_exito(query, max_results=10, headless=True):
    """
    Scraper ajustado para exito usando selectores detectados en el HTML proporcionado.
    - Card selector: article[class*="productCard"]
    - Title: h3.styles_name__qQJiK
    - Link: a[data-testid="product-link"] -> href (relativo)
    - Image: a[data-testid="product-link"] img -> src
    - Price: p.ProductPrice_container__price__XmMWA
    """
    results = []
    with sync_playwright() as pw:
        browser, page = _make_page(pw, headless=headless)
        try:
            url = f"{EXITO_BASE}/s?q=={query}"
            #print url
            page.goto(url)
            # esperar un poco para que cargue JS y productos
            page.wait_for_timeout(10000)

            # selector de tarjetas robusto (busca cualquier clase que contenga productCard)
            cards = page.query_selector_all('article[class*="productCard"], article[class*="productCard_productCard"], article.productCard_productCard__M0677')
            if not cards:
                # fallback más amplio
                cards = page.query_selector_all('article, div[class*="product"], li[class*="product-item"]')

            for c in cards[:max_results]:
                try:
                    title_el = c.query_selector('h3.styles_name__qQJiK, h3, h2')
                    link_el = c.query_selector('a[data-testid="product-link"], a[href]')
                    img_el = c.query_selector('a[data-testid="product-link"] img, img')
                    price_el = c.query_selector('p[data-fs-container-price-otros="true"], p[data-fs-container-price-otros="true"].ProductPrice_container__price__XmMWA')
                    title = title_el.inner_text().strip() if title_el else None
                    price_raw = price_el.inner_text().strip() if price_el else None

                    href = link_el.get_attribute('href') if link_el else None
                    # convertir link relativo a absoluto
                    if href and href.startswith('/'):
                        href = urljoin(EXITO_BASE, href)

                    img = img_el.get_attribute('src') if img_el else None
                    # algunas imágenes están en data-src u otros atributos; intentar extras
                    if img is None and img_el:
                        img = img_el.get_attribute('data-src') or img_el.get_attribute('data-lazy-src')

                    item = {
                        "store": "exito",
                      #  "url": url,
                        "title": title,
                        "price_raw": price_raw,
                        "price": _normalize_price(price_raw) if price_raw else None,
                        "link": href,
                        "img": img
                    }
                    results.append(item)
                except Exception:
                    # no detener todo si una tarjeta falla; seguir con la siguiente
                    continue
        except PWTimeout:
            pass
        finally:
            browser.close()
    return results

def _normalize_price(price_str):
    """Convierte '$ 28.900' ? 28900.0"""
    if not price_str:
        return None
    import re
    digits = re.sub(r'[^\d]', '', price_str)
    try:
        return float(digits)
    except ValueError:
        return None

def scrape_all(query, max_per_store=6, headless=True):
    # ejecutar scrapers secuencial (puedes paralelizar)
    out = {}
    out['farmatodo'] = scrape_farmatodo(query, max_results=max_per_store, headless=headless)
    out['pasteur'] = scrape_pasteur(query, max_results=max_per_store, headless=headless)
    out['cruzverde'] = scrape_cruzverde(query, max_results=max_per_store, headless=headless)
    out['rebaja'] = scrape_rebaja(query, max_results=max_per_store, headless=headless)
    out['exito'] = scrape_exito(query, max_results=max_per_store, headless=headless)
    return out
