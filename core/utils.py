import re
import requests
from tenacity import retry, stop_after_attempt, wait_random

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com",
}

@retry(stop=stop_after_attempt(2), wait=wait_random(min=1, max=3))
def safe_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            raise Exception("Blocked")
        return r
    except:
        return None

def extract_emails(text):
    if not text:
        return []
    return list(set(re.findall(EMAIL_REGEX, text.lower())))
