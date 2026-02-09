import pandas as pd

def dedupe(df):

    df["key"] = df["title"].str.lower() + df["area_sqft"].astype(str)

    df = df.drop_duplicates(subset="key")

    return df.drop(columns=["key"])
