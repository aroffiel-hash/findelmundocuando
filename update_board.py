import os
import json
import sys
import requests
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

def fetch_headlines():
    """Obtiene titulares recientes de Al Jazeera RSS para contexto."""
    try:
        r = requests.get("https://www.aljazeera.com/xml/rss/all.xml", timeout=10)
        headlines = []
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.content)
        for item in root.iter("item"):
            title = item.find("title")
            if title is not None and title.text:
                headlines.append(title.text.strip())
            if len(headlines) >= 20:
                break
        return headlines
    except Exception:
        return []

SYSTEM_PROMPT = """Eres un analista OSINT de riesgo geopolítico de nivel senior.
Tu trabajo es producir un tablero de inteligencia original - NO es un mirror de Polymarket.
El valor del tablero esta en escenarios de cascada, analisis de segunda derivada y contexto
que los mercados de prediccion no cubren bien. Responde UNICAMENTE con JSON valido, sin markdown."""

def build_user_prompt(today, headlines):
    news_block = "\n".join(f"- {h}" for h in headlines[:15]) if headlines else "(sin titulares disponibles)"
    return f"""
Fecha actual: {today}

TITULARES RECIENTES (Al Jazeera):
{news_block}

---
INSTRUCCIONES ANALITICAS:

1. El tablero NO debe duplicar lo que ya esta en Polymarket.
   Polymarket cubre bien: elecciones, resultados binarios, precios de activos.
   Este tablero debe cubrir: escenarios de cascada, riesgos nucleares, colapso institucional,
   efectos geopoliticos en Mexico, y eventos de cola que los mercados subestiman.

2. Para cada apuesta, el campo "params" debe ser ANALITICO:
   - Explicar el mecanismo causal concreto (no solo "probable por la situacion")
   - Citar condiciones necesarias para que ocurra
   - Mencionar el factor que mas podria cambiar la cuota

3. Las cuotas deben reflejar:
   - Historial base rate (cuantas veces ha ocurrido algo asi antes?)
   - Dependencias cruzadas (si X ocurre, como cambia Y?)
   - Asimetria informacional (que sabe un analista que el mercado no?)

4. Secciones OBLIGATORIAS:
   ESCENARIOS MACRO, IRAN Y ORIENTE MEDIO, RUSIA/UCRANIA, CHINA/TAIWAN,
   COREA DEL NORTE, PAKISTAN/AFGANISTAN, EE.UU. INTERIOR,
   MEXICO Y LATAM, ECONOMIA Y ENERGIA, RIESGOS EXISTENCIALES

5. Mexico en particular debe incluir:
   - Impacto de aranceles Trump en manufactura y T-MEC
   - Dependencia de remesas y vulnerabilidad a recesion en EE.UU.
   - Riesgo operativo de carteles en contexto de distraccion del gobierno
   - Postura de Sheinbaum en politica exterior y su costo geopolitico

6. El "ticker" debe tener 12-16 titulares en espanol mexicano, estilo FT no CNN.

ESTRUCTURA JSON EXACTA:
{{
  "lastUpdated": "{today}",
  "ticker": ["titular 1", "titular 2"],
  "methodology": "Parrafo explicando el metodo de este ciclo.",
  "sources": [
    {{"name": "Al Jazeera RSS", "description": "Titulares del ciclo actual.", "url": "https://aljazeera.com"}},
    {{"name": "Groq / LLaMA 3.3-70B", "description": "Modelo de sintesis analitica.", "url": "https://groq.com"}}
  ],
  "sections": [
    {{
      "flag": "emoji",
      "label": "NOMBRE SECCION",
      "rows": [
        {{
          "event": "Escenario especifico",
          "odds": "-150",
          "moved": "down",
          "params": "Analisis causal con base rate historica y factor critico."
        }}
      ]
    }}
  ]
}}

Minimo 6 rows por seccion. SOLO JSON. Sin texto adicional.
"""

def main():
    if not GROQ_API_KEY:
        print("No se encontro GROQ_API_KEY.")
        sys.exit(1)

    today = datetime.utcnow().strftime("%d de %B de %Y - %H:%M UTC")

    print("Obteniendo titulares de Al Jazeera...")
    headlines = fetch_headlines()
    print(f"  {len(headlines)} titulares obtenidos.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_user_prompt(today, headlines)},
        ],
        "temperature": 0.45,
        "max_tokens": 8000,
        "response_format": {"type": "json_object"},
    }

    try:
        print("Generando analisis con Groq LLaMA 3.3-70B...")
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]

        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data  = json.loads(clean)

        data["lastUpdated"] = today
        data.setdefault("sections", [])
        data.setdefault("ticker", ["Actualizando fuentes..."])
        data.setdefault("sources", [
            {"name": "Groq / LLaMA 3.3-70B", "description": "Modelo de sintesis analitica.", "url": "https://groq.com"},
            {"name": "Al Jazeera RSS", "description": "Titulares para contexto.", "url": "https://aljazeera.com"},
        ])

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        total_rows = sum(len(s.get("rows", [])) for s in data["sections"])
        print(f"Exito. {len(data['sections'])} secciones, {total_rows} escenarios.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
