import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from pytrends.request import TrendReq

def get_trending_vintage_keywords():
    print("🔄 1. Scanne Google Trends nach aktuellen Vintage- & Y2K-Streetwear-Trends...")
    pytrends = TrendReq(hl='de-DE', tz=360)
    
    # Präzise Auswahl für den echten Vintage- und Racing-Vibe (cleaner 90s/Y2K Look)
    seed_keywords = [
        "Vintage Racing Jacket",
        "Lucky Strike Jacke",
        "Vintage Avirex",
        "Y2K Lederjacke"
    ]
    
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
                            
        if not trending_terms:
            raise Exception("Keine neuen Google-Trends Ausreißer.")
            
    except Exception:
        # Bombensicheres Backup mit reinen Vintage-Vibe-Klassikern
        trending_terms = [
            "Lucky Strike Lederjacke", 
            "NASCAR Jacket Vintage", 
            "Avirex Leather Jacket", 
            "90s Leather Racing Jacket"
        ]
        print("ℹ️ Nutze vordefinierte Vintage-Trend-Kandidaten für den Scan.")
        
    print(f"🔥 Aktuelle Vintage-Suchbegriffe geladen: {trending_terms}\n")
    return trending_terms

def ebay_vintage_scanner(search_term, max_price):
    print(f"🕵️‍♂️ Scanne eBay nach: '{search_term}' bis max. {max_price}€...")
    
    url = f"https://www.ebay.de/sch/i.html?_nkw={search_term.replace(' ', '+')}&_sop=10&_udhi={max_price}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('li', class_='s-item s-item__pl-on-bottom')
        
        deals = []
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
                    
                deals.append({
                    "Trend-Suchbegriff": search_term,
                    "Artikelname": title,
                    "Preis": price,
                    "Link": link
                })
        return deals
    except Exception as e:
        print(f"❌ Fehler beim eBay-Scan für '{search_term}': {e}")
        return []

if __name__ == "__main__":
    print("==================================================")
    print("🚀 STARTING VINTAGE FLIP BOT (Trends -> eBay Scraper)")
    print("==================================================\n")
    
    # 1. Trends holen
    trends = get_trending_vintage_keywords()
    
    all_found_deals = []
    max_preis_schmerzgrenze = 120  # Hier deine maximale Schmerzgrenze in Euro eintragen
    
    # 2. Schleife über alle Trends
    for trend in trends:
        found_deals = ebay_vintage_scanner(trend, max_preis_schmerzgrenze)
        all_found_deals.extend(found_deals)
        time.sleep(2)  # Kurze Pause zum Schutz vor IP-Sperren
        print("-" * 50)
        
    # 3. Endergebnis anzeigen
    print("\n📊 SCAN-ERGEBNISSE:")
    if all_found_deals:
        df = pd.DataFrame(all_found_deals)
        print(f"🎉 Insgesamt {len(df)} potenzielle Schnäppchen gefunden!\n")
        # Zeige die wichtigsten Spalten im Terminal
        print(df[["Trend-Suchbegriff", "Artikelname", "Preis"]].to_string(index=False))
        
        # Optional: Speicher es direkt als CSV ab
        df.to_csv("aktuelle_ebay_schnaeppchen.csv", index=False, encoding='utf-8')
        print("\n💾 Alle Treffer wurden zusätzlich in 'aktuelle_ebay_schnaeppchen.csv' gespeichert!")
    else:
        print("ℹ️ Aktuell keine neuen Treffer unter der Preisgrenze auf eBay gefunden.")
    
    print("\n✅ Fertig! Schnapp dir die Bilder der Treffer und jage sie durch die Vinted-Bildersuche.")