import os
import json
import sys
import requests
from datetime import datetime, timedelta

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def main():
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY no configurada.")
        sys.exit(1)

    utc_now = datetime.utcnow()
    cdmx_now = utc_now - timedelta(hours=6)

    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    mes_espanol = meses[cdmx_now.month]

    today = cdmx_now.strftime(f"%d de {mes_espanol} de %Y — %H:%M CDMX")
    
    prompt = f"""
    Fecha actual: {today}
    Genera un JSON para el tablero geopolítico "FIN DEL MUNDO - TABLERO DE PROBABILIDADES".
    Redacta en español mexicano neutro y periodístico. Usa el término 'momios'.
    
    Estructura EXACTA requerida:
    {{
      "lastUpdated": "{today}",
      "ticker": ["⚡ Noticia urgente 1...", "🔴 Noticia urgente 2..."],
      "sections": [
        {{
          "flag": "🌍",
          "label": "ESCENARIOS MACRO",
          "rows": [
            {{"event": "Conflicto escala", "odds": "-150", "moved": "down", "params": "Razón breve"}}
          ]
        }}
      ]
    }}
    Genera entre 10 y 14 secciones de riesgo global usando noticias reales de hoy.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Eres un analista de inteligencia geopolítica en México. Respondes ÚNICAMENTE con formato JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"}
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)
        
        # Captura el mensaje exacto de la API si hay error
        if r.status_code != 200:
            print(f"Error de la API: Código {r.status_code} - {r.text}")
            sys.exit(1)
            
        raw = r.json()["choices"][0]["message"]["content"]

        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)

        data["lastUpdated"] = today
        
        if "sections" not in data: 
            data["sections"] = []
        if "ticker" not in data: 
            data["ticker"] = ["⚡ Actualizando fuentes de inteligencia..."]

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Tablero actualizado. Secciones: {len(data.get('sections', []))}")

    except Exception as e:
        print(f"Error de ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
