import os
import json
import sys
import requests
from datetime import datetime

# Configuración de API
API_KEY = os.environ.get("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

def update_board():
    today = datetime.now().strftime("%d de %B de %Y — %H:%M UTC")
    
    # El prompt le pide a la IA que use noticias reales de marzo 2026 y mantenga el formato
    prompt = {
        "contents": [{
            "parts": [{
                "text": f"Eres un analista senior de inteligencia. Hoy es {today}. Genera un JSON estrictamente válido para un Geopolitical Odds Board. "
                        "Debe incluir: 1) 'ticker' con 15 noticias cortas reales con emojis. "
                        "2) 'sections' con 14 categorías (Macro, Irán, México, Cuba, Ucrania, Taiwán, Afganistán, Pakistán, China, Rusia, Corea del Norte, Interior EE.UU., Economía, Longshots). "
                        "Cada categoría debe tener 'flag', 'label' y 'rows' (con 'event', 'odds' tipo -150/+200, 'moved' y 'params'). "
                        "3) 'lastUpdated': '{today}'. Responde SOLO el objeto JSON, sin markdown."
            }]
        }]
    }

    try:
        response = requests.post(URL, json=prompt)
        response.raise_for_status()
        result = response.json()
        
        # Extraer el texto del JSON que devuelve Gemini
        raw_text = result['candidates'][0]['content']['parts'][0]['text']
        # Limpiar posibles bloques de código markdown
        clean_json = raw_text.strip().replace('```json', '').replace('```', '')
        
        data = json.loads(clean_json)
        data["lastUpdated"] = today # Asegurar fecha correcta

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Tablero actualizado con éxito el {today}")

    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: GEMINI_API_KEY no configurada en Secrets")
        sys.exit(1)
    update_board()
