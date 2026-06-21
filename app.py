import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pytrends.request import TrendReq

# Seiteneinstellungen
st.set_page_config(page_title="Vintage Flip Bot", page_icon="🔥", layout="wide")

# UI-Titel (damit die Seite nicht leer aussieht)
st.title("🔥 Vintage & Y2K Streetwear Flip-Bot")
st.write("Drücke den Button, um die aktuellsten Trends zu scannen und eBay zu durchsuchen.")

# Einstellungen in der Seitenleiste
st.sidebar.header("⚙️ Einstellungen")
max_preis = st.sidebar.slider("Maximalpreis (€)", min_value=10, max_value=200, value=50, step=5)

def get_trending_vintage_keywords():
    pytrends = TrendReq(hl='de-DE', tz=360)
    seed_keywords = ["Vintage Racing Jacket", "Lucky Strike Jacke", "Vintage Avirex", "Y2K Lederjacke"]
    trending_terms = []
    try:
        pytrends.build_payload(seed_keywords, timeframe='now 7-d', geo='AT')
        related_queries = pytrends.related_queries()
        for keyword in seed_keywords:
            if keyword in related_queries and 'rising' in related_queries[keyword]:
                rising_df = related_queries[keyword]['rising']
                if rising_df is not None and not rising_df.empty:
                    for index, row in rising_df.head(2).iterrows():
                        query = row['query']
                        if query not in trending_terms:
                            trending_terms.append(query)
    except Exception:
        pass
    
    if not trending_terms:
        trending_terms = ["Lucky Strike Lederjacke", "NASCAR Jacket Vintage", "Avirex Leather Jacket", "90s Leather Racing Jacket"]
    return trending_terms

def ebay_vintage_scanner(search_term, max_price):
    url = f"https://www.ebay.de/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sop=10&_udhi={max_price}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    deals = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='s-item s-item__pl-on-bottom')
        for item in items:
            title_box = item.find('div', class_='s-item__title')
            price_box = item.find('span', class_='s-item__price')
            link_box = item.find('a', class_='s-item__link')
            if title_box and price_box and link_box:
                title = title_box.text.strip()
                price = price_box.text.strip()
                link = link_box['href'].split('?')[0]
                if "Shop on eBay" in title:
                    continue
                deals.append({"Trend": search_term, "Artikelname": title, "Preis": price, "Link": link})
    except Exception:
        pass
    return deals

# Start des Scans
if st.button("🔍 Trends & eBay jetzt live scannen", type="primary"):
    with st.spinner("Hole aktuelle Trends und durchsuche eBay..."):
        trends = get_trending_vintage_keywords()
        st.write(f"📈 **Aktuelle Suchbegriffe:** {', '.join(trends)}")
        
        all_deals = []
        for trend in trends:
            all_deals.extend(ebay_vintage_scanner(trend, max_preis))
            time.sleep(1)
            
        if all_deals:
            df = pd.DataFrame(all_deals)
            st.success(f"🎉 {len(df)} potenzielle Schnäppchen gefunden!")
            st.dataframe(
                df, 
                column_config={"Link": st.column_config.LinkColumn("eBay Link")},
                use_container_width=True
            )
        else:
            st.info("ℹ️ Aktuell keine Treffer unter der Preisgrenze auf eBay.")
