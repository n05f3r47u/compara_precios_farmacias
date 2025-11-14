import asyncio
import re
from browser import get_browser_page

# -------------------------
#   NORMALIZADOR
# -------------------------
def normalize_price(text):
    if not text:
        return None
    t = re.sub(r"[^\d,\.]", "", text)
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except:
        return None


# -------------------------
#   SCRAPERS INDIVIDUALES
# -------------------------

async def scrape_farmatodo(page, query, max_results):
    url = f"https://www.farmatodo.com.co/buscar?product={query}&departamento=Todos&filtros="
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

    return results


async def scrape_rebaja(page, query, max_results):
    url = f"https://www.larebajavirtual.com/search?query={query}"
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

    return results


async def scrape_cruzverde(page, query, max_results):
    url = f"https://www.cruzverde.com.co/search?query={query}"
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

    return results


async def scrape_pasteur(page, query, max_results):
    url = f"https://www.farmaciaspasteur.com.co/{query}?_q={query}&map=ft"
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

    return results


async def scrape_exito(page, query, max_results):
    url = f"https://www.exito.com/s?q={query}"
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

    return results


# -------------------------
#  PARALLEL MASTER SCRAPER
# -------------------------

async def scrape_all(query, max_results=6):

    # Crear un navegador global
    browser_page_pairs = await asyncio.gather(
        get_browser_page(),
        get_browser_page(),
        get_browser_page(),
        get_browser_page(),
        get_browser_page()
    )

    # 5 páginas, una por tienda
    pages = [p for (b, p) in browser_page_pairs]
    browsers = [b for (b, p) in browser_page_pairs]

    tasks = [
        scrape_farmatodo(pages[0], query, max_results),
        scrape_pasteur(pages[1], query, max_results),
        scrape_cruzverde(pages[2], query, max_results),
        scrape_rebaja(pages[3], query, max_results),
        scrape_exito(pages[4], query, max_results),
    ]

    results = await asyncio.gather(*tasks)

    # Cerrar todos los navegadores
    for b in browsers:
        await b.close()

    return {
        "farmatodo": results[0],
        "pasteur": results[1],
        "cruzverde": results[2],
        "rebaja": results[3],
        "exito": results[4],
    }
