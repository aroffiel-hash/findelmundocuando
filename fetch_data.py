import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

def fetch_ticker_news():
    # Jala noticias globales y les inyecta emojis según el contexto
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req).read()
        root = ET.fromstring(response)
        items = root.findall('.//item')
        
        headlines = []
        for item in items[:15]:
            title = item.find('title').text
            low_title = title.lower()
            
            # Asignador inteligente de emojis
            if any(w in low_title for w in ["war", "dead", "attack", "strike", "military", "gaza", "russia", "ukraine", "iran", "israel", "missile"]):
                emoji = "🔴"
            elif any(w in low_title for w in ["market", "economy", "oil", "bank", "fed", "inflation", "brent"]):
                emoji = "📉"
            elif any(w in low_title for w in ["president", "election", "vote", "trump", "biden", "putin", "zelenskyy"]):
                emoji = "🏛️"
            else:
                emoji = "⚡"
                
            headlines.append(f"{emoji} {title}")
        return headlines
    except Exception as e:
        return ["🔴 Error conectando a red de noticias", "⚡ Sincronizando feed geopolítico..."]

def fetch_polymarket_odds():
    # Jala los top 100 eventos de Polymarket para que NUNCA esté vacío
    url = "https://gamma-api.polymarket.com/events?closed=false&limit=100"
    
    sections_dict = {
        "GEOPOLÍTICA Y CONFLICTO": {"keywords": ["war", "military", "missile", "russia", "ukraine", "israel", "iran", "gaza", "taiwan", "china", "korea", "putin", "zelensky"], "rows": []},
        "ECONOMÍA Y RECURSOS": {"keywords": ["oil", "gas", "fed", "rate", "inflation", "economy", "brent", "bitcoin", "crypto", "market", "bank"], "rows": []},
        "POLÍTICA INTERNACIONAL": {"keywords": ["president", "election", "trump", "biden", "harris", "minister", "senate", "cabinet", "court"], "rows": []},
        "ESCENARIOS GLOBALES": {"keywords": [""], "rows": []} # Fallback para rellenar
    }
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        for event in data:
            title = event.get('title', '')
            markets = event.get('markets', [])
            if not markets: continue
            
            # Convierte prob decimal a momio americano
            prob = markets[0].get('probability', 0.5)
            if prob > 0.5:
                odds = int(- (prob / (1 - prob)) * 100)
            else:
                odds = int(((1 - prob) / max(prob, 0.0001)) * 100) # Previene división por cero
                
            odds_str = f"+{odds}" if odds > 0 else str(odds)
            
            # Clasificación
            placed = False
            for sec_name, sec_data in sections_dict.items():
                if sec_name != "ESCENARIOS GLOBALES" and any(kw in title.lower() for kw in sec_data["keywords"]):
                    sec_data["rows"].append({"event": title, "odds": odds_str, "params": "Fuente: Polymarket API", "moved": "none"})
                    placed = True
                    break
            
            if not placed and len(sections_dict["ESCENARIOS GLOBALES"]["rows"]) < 8:
                sections_dict["ESCENARIOS GLOBALES"]["rows"].append({"event": title, "odds": odds_str, "params": "Fuente: Polymarket API", "moved": "none"})

        # Limpiar y preparar JSON final
        final_sections = []
        for label, data in sections_dict.items():
            if len(data["rows"]) > 0:
                final_sections.append({
                    "label": label,
                    "rows": data["rows"][:6] # Solo los 6 más relevantes por sección
                })
                
        return final_sections
    except Exception as e:
        print("Error fetching odds:", e)
        return [{"label": "ERROR DE SISTEMA", "rows": [{"event": "No se pudieron obtener datos del API", "odds": "N/A", "params": "Verifica fetch_data.py", "moved": "none"}]}]

if __name__ == "__main__":
    data = {
        "lastUpdated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ticker": fetch_ticker_news(),
        "sections": fetch_polymarket_odds()
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ data.json generado con éxito y lleno de datos.")
