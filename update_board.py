import os
import json
import sys
import requests
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def main():
    if not GROQ_API_KEY:
        print("❌ Error: No se encontró GROQ_API_KEY en las variables de entorno.")
        sys.exit(1)

    today = datetime.utcnow().strftime("%d de %B de %Y — %H:%M UTC")
    
    prompt = f"""
    Fecha actual: {today}
    Genera un JSON para el tablero geopolítico "Fin del Mundo Cuándo".
    Usa noticias reales y crudas de hoy. Devuelve SOLO el JSON.
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
    Importante: Genera entre 8 y 14 secciones de riesgo global.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Eres un analista de inteligencia geopolítica. Respondes ÚNICAMENTE con JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]

        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)

        data["lastUpdated"] = today
        
        # Salvavidas: si falta algo, pone valores por defecto pero NO rompe el código
        if "sections" not in data:
            data["sections"] = []
        if "ticker" not in data:
            data["ticker"] = ["⚡ Actualizando fuentes satelitales..."]

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Éxito. {len(data.get('sections', []))} secciones generadas.")

    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
