def property_score(row):

    score = 0

    try:
        price = float(row.get("price",0))
        area = float(row.get("area_sqft",0))
    except:
        price = area = 0

    if area > 1000:
        score += 25

    if price and price < 8000000:
        score += 25

    if "owner" in row.get("posted_by","").lower():
        score += 20

    if row.get("emails"):
        score += 15

    if "apartment" in row.get("type","").lower():
        score += 10

    return min(score,100)
