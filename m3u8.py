import asyncio
import time
import re
from playwright.async_api import async_playwright, TimeoutError as PWTimeout


# -----------------------------
# helpers
# -----------------------------
def parse_expiry(m3u8_url: str):
    match = re.search(r"end=(\d+)", m3u8_url)
    if not match:
        return None, None

    expiry_ts = int(match.group(1))
    now = int(time.time())
    remaining = expiry_ts - now

    if remaining <= 0:
        return remaining, "EXPIRED"

    return remaining, f"{remaining // 60}m {remaining % 60}s"


def extract_qualities(m3u8_url: str):
    """
    Build real playable links per quality
    """
    match = re.search(r"multi=([^/]+)/", m3u8_url)
    if not match:
        return []

    qualities = []
    base = m3u8_url.split("multi=")[0]
    tail = m3u8_url.split(match.group(0))[1]

    entries = match.group(1).split(",")

    for entry in entries:
        res, label = entry.split(":")[:2]
        url = f"{base}{res}/{tail.replace('_TPL_', res)}"

        qualities.append({
            "label": label,
            "resolution": res,
            "url": url
        })

    return qualities


# -----------------------------
# playwright scraper
# -----------------------------
async def capture_m3u8(url: str):
    found_event = asyncio.Event()
    found_url = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        def on_request(request):
            nonlocal found_url
            if ".m3u8" in request.url and not found_url:
                found_url = request.url
                found_event.set()

        page.on("request", on_request)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.wait_for(found_event.wait(), timeout=15)

        except (asyncio.TimeoutError, PWTimeout):
            pass

        finally:
            await browser.close()

    return found_url


# -----------------------------
# sync wrapper
# -----------------------------
def get_m3u8(url: str):
    m3u8 = asyncio.run(capture_m3u8(url))
    if not m3u8:
        return None

    remaining, readable = parse_expiry(m3u8)

    return {
        "m3u8": m3u8,
        "expires_in": remaining,
        "expires_readable": readable,
        "qualities": extract_qualities(m3u8)
    }


# local test
if __name__ == "__main__":
    test = get_m3u8("PASTE_TEST_URL_HERE")
    print(test)
