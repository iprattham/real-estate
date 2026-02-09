import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

# Force Playwright to use system Chromium (Streamlit Cloud)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

BASE = "https://housing.com"

def clean_area(v):
    return re.sub("[^0-9]", "", v)

def scrape_housing(city="noida", limit=10):

    url = f"{BASE}/in/buy/{city}"

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            )
        )

        # Speed: block images + fonts
        context.route(
            "**/*",
            lambda route, request:
                route.abort() if request.resource_type in ["image", "font"]
                else route.continue_()
        )

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        # Scroll to load listings
        for _ in range(4):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1500)

        soup = BeautifulSoup(page.content(), "lxml")

        cards = soup.select("article")

        for c in cards[:limit]:

            try:
                href = c.find("a")["href"]

                if href.startswith("http"):
                    link = href
                else:
                    link = BASE + href

                title = c.get_text(strip=True)[:100]

                results.append({
                    "title": title,
                    "price": "",
                    "area_sqft": "",
                    "location": city,
                    "type": "Apartment",
                    "posted_by": "Broker",
                    "emails": [],
                    "url": link
                })

            except Exception as e:
                print("Skipped housing listing:", e)
                continue

        browser.close()

    return results
