import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

BASE = "https://housing.com"

def clean_area(v):
    return re.sub("[^0-9]", "", v)

def scrape_housing(city="noida", limit=20, headless=True):

    url = f"{BASE}/in/buy/{city}"

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_timeout(4000)

        for _ in range(4):
            page.mouse.wheel(0, 4000)
            page.wait_for_timeout(1500)

        soup = BeautifulSoup(page.content(), "lxml")

        cards = soup.select("article")

        for c in cards[:limit]:

            try:
                link = BASE + c.find("a")["href"]

                title = c.text[:80]

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

            except:
                continue

        browser.close()

    return results
