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
    Genera un JSON actualizado para el tablero geopolítico.
    Estructura EXACTA requerida:
    {{
      "lastUpdated": "{today}",
      "ticker": ["⚡ Noticia 1", "🔴 Noticia 2", "15 noticias en total"],
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
    Instrucciones:
    - Genera al menos 10-14 secciones (Macro, Irán, México, Economía, etc).
    - Usa noticias geopolíticas de alta tensión de marzo 2026.
    - Devuelve ÚNICAMENTE JSON válido. Nada de markdown.
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Eres un analista OSINT experto. Solo respondes en JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    try:
        print("📡 Conectando a Groq (Llama 3)...")
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=90)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]

        # Limpieza básica por si la IA devuelve markdown
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)

        # Inyectar fecha sí o sí
        data["lastUpdated"] = today
        
        # Validar mínimo viable sin romper el programa si faltan secciones
        if "sections" not in data:
            data["sections"] = []
        if "ticker" not in data:
            data["ticker"] = ["⚡ Actualizando fuentes satelitales..."]

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Éxito. {len(data['sections'])} secciones generadas.")

    except Exception as e:
        print(f"❌ Error fatal durante la generación o procesado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
