from scrapers.magicbricks import scrape_magicbricks

data = scrape_magicbricks("Noida", 5, headless=False)

for d in data:
    print(d)
