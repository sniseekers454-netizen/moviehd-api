import asyncio
from playwright.async_api import async_playwright

async def capture_m3u8(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chromium",   # 🔑 IMPORTANT
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = await browser.new_page()
        m3u8_url = None

        async def handle_response(response):
            nonlocal m3u8_url
            if ".m3u8" in response.url:
                m3u8_url = response.url

        page.on("response", handle_response)

        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)

        await browser.close()
        return m3u8_url


def get_m3u8(url):
    try:
        m3u8 = asyncio.run(capture_m3u8(url))
        if not m3u8:
            return None

        return {
            "m3u8": m3u8
        }

    except Exception as e:
        print("❌ M3U8 ERROR:", e)
        return None
