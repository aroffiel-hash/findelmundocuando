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
    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    today = cdmx_now.strftime(f"%d de {meses[cdmx_now.month]} de %Y — %H:%M CDMX")
    
    prompt = f"Fecha: {today}. Genera un JSON para el tablero 'FIN DEL MUNDO - TABLERO DE PROBABILIDADES'. Usa noticias reales. Incluye 'lastUpdated', 'ticker' (lista de noticias cortas) y 'sections' (lista con 'flag', 'label' y 'rows'). En 'rows' cada objeto debe tener 'event', 'odds', 'moved' (up/down/none) y 'params'. Redacta en español mexicano."

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres un analista geopolítico. Respondes SOLO con JSON válido."},
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
            
        data = r.json()["choices"][0]["message"]["content"]
        final_data = json.loads(data)
        final_data["lastUpdated"] = today

        if "sections" not in final_data: final_data["sections"] = []
        if "ticker" not in final_data: final_data["ticker"] = ["⚡ Actualizando datos de inteligencia..."]

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print("Actualización exitosa.")
    except Exception as e:
        print(f"Error de ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
