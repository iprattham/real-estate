def calculate_roi(row):

    try:
        price = float(row["price"]) * 10000000  # Cr → INR
        area = float(row["area_sqft"])
    except:
        return 0

    monthly_rent = area * 40   # ₹40/sqft heuristic

    yearly = monthly_rent * 12

    roi = (yearly / price) * 100

    return round(roi,2)
