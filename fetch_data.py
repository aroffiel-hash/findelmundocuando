import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

def fetch_ticker_news():
    # Jala noticias frescas de un RSS global (ej. Al Jazeera o similar)
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        root = ET.fromstring(response)
        items = root.findall('.//item')
        return [item.find('title').text for item in items[:10]]
    except:
        return ["⚠️ Señal de noticias interrumpida", "Sincronizando feed geopolítico..."]

def fetch_polymarket_odds():
    # Jala momios reales de Polymarket (Gamma API)
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=50"
    sections = [
        {"label": "ORIENTE MEDIO", "keywords": ["Israel", "Iran", "Gaza", "Middle East"], "rows": []},
        {"label": "EUROPA DEL ESTE", "keywords": ["Russia", "Ukraine", "Putin"], "rows": []},
        {"label": "INDO-PACÍFICO", "keywords": ["China", "Taiwan", "US"], "rows": []},
        {"label": "MERCADOS GLOBALES", "keywords": ["Oil", "Fed", "Economy", "Bitcoin"], "rows": []}
    ]
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets: continue
            
            # Convierte la probabilidad de Polymarket (0.0 a 1.0) a Momio Americano
            prob = markets[0].get('probability', 0.5)
            if prob > 0.5:
                odds = int(- (prob / (1 - prob)) * 100)
            else:
                odds = int(((1 - prob) / prob) * 100)
                
            odds_str = f"+{odds}" if odds > 0 else str(odds)
            
            # Clasifica el evento en su sección
            for sec in sections:
                if any(kw.lower() in title.lower() for kw in sec['keywords']):
                    sec['rows'].append({
                        "event": title,
                        "odds": odds_str,
                        "params": "Fuente: Polymarket API",
                        "moved": "none"
                    })
                    break
                    
        # Filtra secciones vacías y recorta a los 5 eventos más importantes por sección
        valid_sections = [s for s in sections if len(s['rows']) > 0]
        for s in valid_sections:
            s['rows'] = s['rows'][:5]
            
        return valid_sections
    except Exception as e:
        print("Error fetching odds:", e)
        return []

if __name__ == "__main__":
    data = {
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ticker": fetch_ticker_news(),
        "sections": fetch_polymarket_odds()
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("data.json actualizado correctamente.")
