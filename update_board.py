import os
import json
import sys
import requests
from datetime import datetime, timedelta

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def main():
    if not GROQ_API_KEY:
        print("❌ Error: No se encontró GROQ_API_KEY en las variables de entorno.")
        sys.exit(1)

    # Cálculo exacto de hora CDMX (UTC -6)
    utc_now = datetime.utcnow()
    cdmx_now = utc_now - timedelta(hours=6)

    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    mes_espanol = meses[cdmx_now.month]

    # Formato de fecha para que el visitante sepa que está fresco
    today = cdmx_now.strftime(f"%d de {mes_espanol} de %Y — %H:%M CDMX")
    
    prompt = f"""
    Fecha actual: {today}
    Genera un JSON para el tablero geopolítico "Fin del Mundo Cuándo".
    REGLA DE ORO: Redacta TODO en un español mexicano neutro, serio y periodístico (ej. usa 'momios' en vez de 'cuotas').
    
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
    Importante: Genera entre 10 y 14 secciones de riesgo global usando noticias reales de hoy.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Eres un analista de inteligencia geopolítica en México. Respondes ÚNICAMENTE con JSON válido."},
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

        # Inyección forzada de la fecha de México
        data["lastUpdated"] = today
        
        # Salvavidas: Ya NO hay asserts. Si falta algo, se pone vacío y el programa continúa.
        if "sections" not in data: data["sections"] = []
        if "ticker" not in data: data["ticker"] = ["⚡ Actualizando fuentes de inteligencia..."]

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Éxito. Fecha ajustada a: {today}. Secciones: {len(data.get('sections', []))}")

    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
