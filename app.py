import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import pandas as pd

from scrapers.magicbricks import scrape_magicbricks
from scrapers.housing import scrape_housing

from core.dedupe import dedupe
from core.roi import calculate_roi

st.set_page_config(layout="wide")

st.title("🏠 PropSpy — Real Estate Intelligence Platform")

city = st.text_input("City","Noida")
limit = st.slider("Listings per site",5,30,10)

if st.button("🚀 Run Scrapers"):

    with st.spinner("Scraping..."):

        mb = scrape_magicbricks(city,limit)
        hs = scrape_housing(city.lower(),limit)

        df = pd.DataFrame(mb + hs)

        if df.empty:
            st.error("No properties scraped")
            st.stop()

        df = dedupe(df)

        df["roi_percent"] = df.apply(calculate_roi,axis=1)

        st.success(f"{len(df)} unique properties")

        st.dataframe(df)

        st.subheader("📈 Top ROI Deals")

        st.dataframe(df.sort_values("roi_percent",ascending=False).head(10))

        st.download_button(
            "⬇ Export CSV",
            df.to_csv(index=False),
            "properties.csv"
        )
