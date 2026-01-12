import asyncio
from playwright.async_api import async_playwright

async def capture_m3u8(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chromium",
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

        # ✅ correct load strategy for video sites
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # ✅ wait until video player exists
        await page.wait_for_selector("video", timeout=20000)

        # ✅ allow stream requests to fire
        await asyncio.sleep(12)

        # 🔁 small retry window (extra safety)
        for _ in range(3):
            if m3u8_url:
                break
            await asyncio.sleep(3)

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
