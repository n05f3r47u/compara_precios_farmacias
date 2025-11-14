import asyncio
from pyppeteer import launch

async def get_browser_page():
    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-software-rasterizer",
        ]
    )

    page = await browser.newPage()
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    await page.setViewport({"width": 1280, "height": 900})
    return browser, page
