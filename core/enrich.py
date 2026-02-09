import re

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(?:\+91)?[6-9]\d{9}")

def extract_contacts(text):

    emails = list(set(re.findall(EMAIL_REGEX, text.lower())))
    phones = list(set(re.findall(PHONE_REGEX, text)))

    return emails, phones
