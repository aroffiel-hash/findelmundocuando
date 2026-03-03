import os
import json
import sys
import requests
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def get_real_news():
    # Jala titulares mundiales en tiempo real para dárselos de contexto a la IA
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req).read()
        root = ET.fromstring(resp)
        items = root.findall('.//item')
        return "\n".join([f"- {item.find('title').text}" for item in items[:25]])
    except:
        return "- Tensión en Medio Oriente\n- Mercados petroleros volátiles\n- Elecciones y política global"

def main():
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY no configurada en GitHub Secrets.")
        sys.exit(1)

    utc_now = datetime.utcnow()
    cdmx_now = utc_now - timedelta(hours=6)
    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    today = cdmx_now.strftime(f"%d de {meses[cdmx_now.month]} de %Y — %H:%M CDMX")
    
    # 1. Obtener noticias reales
    news_context = get_real_news()

    # 2. Instruir a la IA
    prompt = f"""Fecha actual: {today}. 
Eres un analista geopolítico experto. 
A partir de los siguientes titulares de noticias de ÚLTIMA HORA:
{news_context}

Genera un JSON ESTRICTO para el 'TABLERO DE PROBABILIDADES GEOPOLÍTICO'.
El JSON debe tener esta estructura exacta (obligatorio):
{{
  "lastUpdated": "{today}",
  "ticker": ["⚡ Noticia urgente 1", "🔴 Noticia urgente 2", "💰 Noticia económica 3"],
  "sections": [
    {{
      "flag": "🌍",
      "label": "NOMBRE DE LA SECCIÓN",
      "rows": [
        {{
          "event": "Escenario probable basado en las noticias",
          "odds": "-150", 
          "moved": "down",
          "params": "Justificación basada en los titulares."
        }}
      ]
    }}
  ]
}}

Reglas Críticas:
1. Crea al menos 5 secciones (ej. MEDIO ORIENTE 🇮🇷, ESTADOS UNIDOS 🇺🇸, ECONOMÍA 💰, UCRANIA/RUSIA 🇷🇺). Usa banderas en 'flag'.
2. En 'odds' usa estricto formato americano (ej. "-200", "+150", o "LIQUIDADO").
3. En 'moved' usa SOLO: "up", "down", o "none".
4. DEBES RESPONDER ÚNICAMENTE CON EL JSON VÁLIDO. Cero texto antes o después.
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres una máquina que solo devuelve JSON válido, sin formato markdown ni explicaciones."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 6000,
        "response_format": {"type": "json_object"}
    }

    try:
        r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json=payload, timeout=90)
        if r.status_code != 200:
            print(f"Error API: {r.text}")
            sys.exit(1)
            
        data_text = r.json()["choices"][0]["message"]["content"]
        final_data = json.loads(data_text)
        final_data["lastUpdated"] = today

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print("✅ data.json generado con éxito por la IA.")
    except Exception as e:
        print(f"Error de ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
