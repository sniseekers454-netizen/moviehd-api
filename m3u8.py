import asyncio
from playwright.async_api import async_playwright


async def capture_m3u8(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--no-zygote"
            ]
        )

        page = await browser.new_page()
        m3u8_url = None

        async def handle_response(response):
            nonlocal m3u8_url
            if m3u8_url:
                return
            if ".m3u8" in response.url:
                m3u8_url = response.url

        page.on("response", handle_response)

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # ⏱ short wait only
            for _ in range(8):
                if m3u8_url:
                    break
                await asyncio.sleep(0.5)

        except Exception as e:
            print("❌ PAGE LOAD ERROR:", e)

        await browser.close()
        return m3u8_url


def get_m3u8(url):
    try:
        m3u8 = asyncio.run(capture_m3u8(url))

        if not m3u8:
            return {"m3u8": None}

        return {"m3u8": m3u8}

    except Exception as e:
        print("❌ M3U8 ERROR:", e)
        return {"m3u8": None}
