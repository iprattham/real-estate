import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

# Force Playwright to use system Chromium (Streamlit Cloud)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

BASE = "https://www.magicbricks.com"

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# ---------------- HELPERS ---------------- #

def extract_emails(text):
    if not text:
        return []
    return list(set(re.findall(EMAIL_REGEX, text.lower())))

def clean_price(val):
    if not val:
        return ""
    return (
        val.replace("₹", "")
        .replace("Cr", "")
        .replace("Lac", "")
        .replace(",", "")
        .strip()
    )

def clean_area(val):
    return re.sub("[^0-9]", "", val)

# ---------------- MAIN SCRAPER ---------------- #

def scrape_magicbricks(city="Noida", limit=10):

    url = f"{BASE}/property-for-sale/residential-real-estate?cityName={city}"

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

        # Speed boost: block images + fonts
        context.route(
            "**/*",
            lambda route, request:
                route.abort() if request.resource_type in ["image", "font"]
                else route.continue_()
        )

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")

        # Scroll to load cards
        for _ in range(4):
            page.mouse.wheel(0, 5000)
            page.wait_for_timeout(1500)

        soup = BeautifulSoup(page.content(), "lxml")

        cards = soup.select(".mb-srp__card")

        for card in cards[:limit]:

            try:
                title_el = card.select_one(".mb-srp__card--title")
                title = title_el.get_text(strip=True) if title_el else ""

                price_el = card.select_one(".mb-srp__card__price--amount")
                price = clean_price(price_el.get_text(strip=True)) if price_el else ""

                area_el = card.select_one(".mb-srp__card__summary--value")
                area = clean_area(area_el.get_text(strip=True)) if area_el else ""

                href = card.find("a")["href"]

                if href.startswith("http"):
                    link = href
                elif href.startswith("/"):
                    link = BASE + href
                else:
                    continue

                # -------- Detail Page -------- #

                detail_page = context.new_page()
                detail_page.goto(link, timeout=40000)
                detail_page.wait_for_load_state("networkidle")

                detail_html = detail_page.content()
                detail_page.close()

                emails = extract_emails(detail_html)

                results.append({
                    "title": title,
                    "price": price,
                    "area_sqft": area,
                    "location": city,
                    "type": "Apartment",
                    "posted_by": "Broker",
                    "emails": emails,
                    "url": link
                })

            except Exception as e:
                print("Skipped listing:", e)
                continue

        browser.close()

    return results
