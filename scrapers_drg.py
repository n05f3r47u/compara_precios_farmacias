import asyncio
import re
from browser import get_browser_page

# Normalizador de precios
def normalize_price(text):
    if not text:
        return None
    t = re.sub(r"[^\d,\.]", "", text)
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return None


# -----------------------------
#  FARMATODO
# -----------------------------
async def scrape_farmatodo(query, max_results=10):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos&filtros="

    browser, page = await get_browser_page()
    await page.goto(url, waitUntil="networkidle2")
    await asyncio.sleep(3)

    cards = await page.querySelectorAll("div.card-ftd__card-unique")
    results = []

    for c in cards[:max_results]:
        try:
            title = await page.evaluate("(el)=>el.innerText", await c.querySelector("p.text-title"))
            price_raw = await page.evaluate("(el)=>el.innerText", await c.querySelector("span.price__text-price"))
            link = await page.evaluate("(el)=>el.href", await c.querySelector("a.content-product"))
            img = await page.evaluate("(el)=>el.src", await c.querySelector("img.product-image__image"))

            results.append({
                "store": "farmatodo",
                "title": title,
                "price_raw": price_raw,
                "price": normalize_price(price_raw),
                "link": link,
                "img": img
            })
        except:
            continue

    await browser.close()
    return results


# -----------------------------
#  REBAJA
# -----------------------------
async def scrape_rebaja(query, max_results=10):
    url = f"https://www.larebajavirtual.com/search?query={query}"

    browser, page = await get_browser_page()
    await page.goto(url, waitUntil="networkidle2")
    await asyncio.sleep(3)

    cards = await page.querySelectorAll("section.vtex-product-summary-2-x-container")
    results = []

    for c in cards[:max_results]:
        try:
            title = await page.evaluate("(el)=>el.innerText", await c.querySelector(".vtex-product-summary-2-x-productNameContainer"))
            price_raw = await page.evaluate("(el)=>el.innerText", await c.querySelector(".vtex-product-price-1-x-sellingPrice"))
            link = await page.evaluate("(el)=>el.href", await c.querySelector("a.vtex-product-summary-2-x-clearLink"))
            img = await page.evaluate("(el)=>el.src", await c.querySelector(".vtex-product-summary-2-x-imageNormal"))

            results.append({
                "store": "rebaja",
                "title": title,
                "price_raw": price_raw,
                "price": normalize_price(price_raw),
                "link": link,
                "img": img
            })
        except:
            continue

    await browser.close()
    return results


# -----------------------------
#  CRUZ VERDE
# -----------------------------
async def scrape_cruzverde(query, max_results=10):
    url = f"https://www.cruzverde.com.co/search?query={query}"

    browser, page = await get_browser_page()
    await page.goto(url, waitUntil="networkidle2")
    await asyncio.sleep(3)

    cards = await page.querySelectorAll("ml-card-product")
    results = []

    for c in cards[:max_results]:
        try:
            title = await page.evaluate("(el)=>el.innerText", await c.querySelector("a.font-open.flex.items-center"))
            price_raw = await page.evaluate("(el)=>el.innerText", await c.querySelector("span.font-bold.text-prices"))
            link = await page.evaluate("(el)=>el.href", await c.querySelector("a.font-open.flex.items-center"))
            img = await page.evaluate("(el)=>el.src", await c.querySelector("img"))

            results.append({
                "store": "cruzverde",
                "title": title,
                "price_raw": price_raw,
                "price": normalize_price(price_raw),
                "link": link,
                "img": img
            })
        except:
            continue

    await browser.close()
    return results


# -----------------------------
#  PASTEUR
# -----------------------------
async def scrape_pasteur(query, max_results=10):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"

    browser, page = await get_browser_page()
    await page.goto(url, waitUntil="networkidle2")
    await asyncio.sleep(3)

    cards = await page.querySelectorAll("div.vtex-flex-layout-0-x-flexCol--col-general-product-info")
    results = []

    for c in cards[:max_results]:
        try:
            title = await page.evaluate("(el)=>el.innerText", await c.querySelector("span.vtex-product-summary-2-x-productBrand"))
            price_raw = await page.evaluate("(el)=>el.innerText", await c.querySelector("span.vtex-product-price-1-x-currencyContainer"))
            link = await page.evaluate("(el)=>el.href", await c.querySelector("a.vtex-product-summary-2-x-clearLink"))
            img = await page.evaluate("(el)=>el.src", await c.querySelector("img.vtex-product-summary-2-x-image"))

            results.append({
                "store": "pasteur",
                "title": title,
                "price_raw": price_raw,
                "price": normalize_price(price_raw),
                "link": link,
                "img": img
            })
        except:
            continue

    await browser.close()
    return results


# -----------------------------
#  EXITO
# -----------------------------
async def scrape_exito(query, max_results=10):
    url = f"https://www.exito.com/s?q={query}"

    browser, page = await get_browser_page()
    await page.goto(url, waitUntil="networkidle2")
    await asyncio.sleep(3)

    cards = await page.querySelectorAll("article[class*='productCard']")
    results = []

    for c in cards[:max_results]:
        try:
            title = await page.evaluate("(el)=>el.innerText", await c.querySelector("h3"))
            price_raw = await page.evaluate("(el)=>el.innerText", await c.querySelector("p"))
            link = await page.evaluate("(el)=>el.href", await c.querySelector("a"))
            img = await page.evaluate("(el)=>el.src", await c.querySelector("img"))

            results.append({
                "store": "exito",
                "title": title,
                "price_raw": price_raw,
                "price": normalize_price(price_raw),
                "link": link,
                "img": img
            })
        except:
            continue

    await browser.close()
    return results


# -----------------------------
#  MASTER SCRAPER
# -----------------------------
async def scrape_all(query, max_results=6):
    return {
        "farmatodo": await scrape_farmatodo(query, max_results),
        "pasteur": await scrape_pasteur(query, max_results),
        "cruzverde": await scrape_cruzverde(query, max_results),
        "rebaja": await scrape_rebaja(query, max_results),
        "exito": await scrape_exito(query, max_results),
    }
