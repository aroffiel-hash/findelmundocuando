import os
import json
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

# ── Fuentes RSS geopolíticas ──────────────────────────────────────────────────
RSS_SOURCES = [
    ("Al Jazeera",  "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Reuters",     "https://feeds.reuters.com/reuters/worldNews"),
    ("BBC World",   "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("AP News",     "https://rsshub.app/apnews/topics/world-news"),
]

# Palabras que indican contenido NO geopolítico — filtrar antes de pasar a la IA
NOISE_KEYWORDS = [
    "oscar","emmy","grammy","super bowl","nba","nfl","nhl","mlb","formula 1",
    "box office","celebrity","entertainment","sports","soccer league","premier league",
    "music award","film festival","box score","playoff","draft pick",
    "reality show","fashion week","album release","concert tour",
]

def is_geopolitical(headline: str) -> bool:
    h = headline.lower()
    if any(k in h for k in NOISE_KEYWORDS):
        return False
    GEO_KEYWORDS = [
        "war","military","missile","russia","ukraine","israel","iran","gaza",
        "taiwan","china","korea","nato","troops","airstrike","nuclear","attack",
        "conflict","ceasefire","sanction","invasion","bomb","coup","protest",
        "election","president","minister","government","treaty","diplomatic",
        "oil","gas","inflation","recession","tariff","trade","economic",
        "refugee","crisis","terror","insurgent","cartel","mexico","latam",
        "pakistan","afghanistan","hezbollah","irgc","hamas","houthi",
        "pentagon","kremlin","white house","congress","un security",
    ]
    return any(k in h for k in GEO_KEYWORDS)

def fetch_all_headlines() -> list:
    all_headlines = []
    for source_name, url in RSS_SOURCES:
        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
            root = ET.fromstring(r.content)
            count = 0
            for item in root.iter("item"):
                title = item.find("title")
                desc  = item.find("description")
                text  = (title.text or "") if title is not None else ""
                if desc is not None and desc.text:
                    text += " — " + desc.text[:120]
                text = text.strip()
                if text and is_geopolitical(text):
                    all_headlines.append(f"[{source_name}] {text}")
                    count += 1
                if count >= 8:
                    break
            print(f"  {source_name}: {count} titulares geopolíticos")
        except Exception as e:
            print(f"  {source_name}: fallo ({e})")
    # Dedup simple
    seen, unique = set(), []
    for h in all_headlines:
        key = h[:60].lower()
        if key not in seen:
            seen.add(key)
            unique.append(h)
    return unique[:30]

SYSTEM_PROMPT = """Eres un analista OSINT de riesgo geopolítico nivel senior.
Produces un tablero de inteligencia ORIGINAL — no un mirror de Polymarket ni de ningún
mercado de predicción. Cada apuesta debe tener valor analítico propio:
mecanismo causal claro, base rate histórica, y el factor que más podría cambiar la cuota.
NUNCA incluyas entretenimiento, deportes, awards, box office, celebrity news ni deportes.
Responde ÚNICAMENTE con JSON válido, sin markdown, sin texto fuera del JSON."""

def build_prompt(today: str, headlines: list) -> str:
    news_block = "\n".join(f"  {h}" for h in headlines) if headlines else "  (sin titulares disponibles)"
    return f"""Fecha actual: {today}

TITULARES GEOPOLÍTICOS EN TIEMPO REAL:
{news_block}

---
GENERA EL TABLERO CON ESTAS REGLAS:

REGLA 1 — ORIGINALIDAD ANALÍTICA
El tablero complementa Polymarket, no lo duplica. Polymarket cubre bien: elecciones,
precios de activos, resultados binarios. Tú cubres:
- Escenarios de cascada y segunda derivada (si X → qué implica para Y, Z)
- Riesgos nucleares e institucionales que los mercados subestiman por sesgo de normalidad
- Efectos geopolíticos en México que no tienen mercado activo
- Eventos de cola: cosas con 5-15% de probabilidad que, si ocurren, son catastróficas

REGLA 2 — CALIDAD DEL CAMPO "params"
Cada params DEBE incluir:
a) Mecanismo causal: ¿por qué específicamente? (no "debido a la tensión")
b) Condición necesaria: ¿qué tiene que pasar primero?
c) Base rate: ¿cuántas veces ha ocurrido algo equivalente en la historia?
d) Factor crítico: ¿qué cambiaría más la cuota?

REGLA 3 — SECCIONES OBLIGATORIAS (exactamente estas, en este orden):
  🌍 ESCENARIOS MACRO
  🇮🇷 IRÁN Y ORIENTE MEDIO
  🇷🇺 RUSIA / UCRANIA
  🇹🇼 CHINA / TAIWÁN
  🇰🇵 COREA DEL NORTE
  🇵🇰 PAKISTÁN / AFGANISTÁN
  🇺🇸 EE.UU. — INTERIOR
  🇲🇽 MÉXICO Y LATAM
  💰 ECONOMÍA Y ENERGÍA
  ☢️ RIESGOS EXISTENCIALES

REGLA 4 — MÉXICO debe incluir (mínimo 1 row por cada):
- Impacto de aranceles Trump en manufactura y T-MEC
- Vulnerabilidad por remesas si EE.UU. entra en recesión
- Riesgo operativo de carteles (aprovechan distracción institucional)
- Postura de Sheinbaum en política exterior (neutralidad vs costo con EE.UU.)
- Peso mexicano y acceso a mercados de capital

REGLA 5 — TICKER: 14 titulares en español mexicano. Tono FT, no CNN.
Concisos, informativos, sin clickbait. Emojis apropiados al tono.

REGLA 6 — CUOTAS: formato americano. Mínimo 6 rows por sección.
Solo usar "moved": "down" (más probable), "up" (menos probable), o null.

ESTRUCTURA JSON REQUERIDA:
{{
  "lastUpdated": "{today}",
  "ticker": ["⚡ Titular preciso 1", "🔴 Titular 2", "...14 total..."],
  "methodology": "Ciclo {today}: análisis basado en {len(headlines)} titulares de {len(RSS_SOURCES)} fuentes RSS internacionales procesados con LLaMA 3.3-70B. Las cuotas reflejan síntesis analítica, no datos de mercado.",
  "sources": [
    {{"name": "Al Jazeera RSS", "description": "Cobertura internacional en tiempo real.", "url": "https://aljazeera.com"}},
    {{"name": "Reuters World News", "description": "Agencia de noticias internacional.", "url": "https://reuters.com"}},
    {{"name": "BBC World", "description": "Cobertura global BBC.", "url": "https://bbc.com/news/world"}},
    {{"name": "Groq / LLaMA 3.3-70B", "description": "Modelo de síntesis analítica.", "url": "https://groq.com"}}
  ],
  "sections": [
    {{
      "flag": "🌍",
      "label": "ESCENARIOS MACRO",
      "rows": [
        {{
          "event": "Descripción precisa y específica del escenario",
          "odds": "-150",
          "moved": "down",
          "params": "a) Mecanismo: [causal específico]. b) Condición: [necesaria]. c) Base rate: [histórica]. d) Factor crítico: [qué cambiaría la cuota]."
        }}
      ]
    }}
  ]
}}

DEVUELVE SOLO EL JSON. Nada antes ni después."""

def main():
    if not GROQ_API_KEY:
        print("Error: no se encontró GROQ_API_KEY.")
        sys.exit(1)

    today = datetime.utcnow().strftime("%d de %B de %Y — %H:%M UTC")

    print("Obteniendo titulares geopolíticos de múltiples fuentes RSS...")
    headlines = fetch_all_headlines()
    print(f"Total: {len(headlines)} titulares geopolíticos filtrados.")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": build_prompt(today, headlines)},
        ],
        "temperature": 0.45,
        "max_tokens": 8192,
        "response_format": {"type": "json_object"},
    }

    try:
        print("Generando análisis con Groq / LLaMA 3.3-70B...")
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        raw  = r.json()["choices"][0]["message"]["content"]
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data  = json.loads(clean)

        # Garantías mínimas
        data["lastUpdated"] = today
        data.setdefault("sections", [])
        data.setdefault("ticker", ["⚡ Actualizando fuentes..."])
        data.setdefault("sources", [
            {"name": "Groq / LLaMA 3.3-70B", "description": "Síntesis analítica.", "url": "https://groq.com"},
        ])
        data.setdefault("methodology", f"Análisis generado el {today} usando LLaMA 3.3-70B.")

        # Filtrar rows de entretenimiento/deportes en post-procesado
        noise = [
            "oscar","emmy","grammy","super bowl","nba","nfl","box office",
            "celebrity","entertainment","sports","award","film festival",
        ]
        for section in data["sections"]:
            original = len(section.get("rows", []))
            section["rows"] = [
                r for r in section.get("rows", [])
                if not any(k in (r.get("event","") + r.get("params","")).lower() for k in noise)
            ]
            removed = original - len(section["rows"])
            if removed:
                print(f"  Filtrado {removed} rows de entretenimiento en '{section['label']}'")

        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        total_rows = sum(len(s.get("rows", [])) for s in data["sections"])
        print(f"Éxito. {len(data['sections'])} secciones, {total_rows} escenarios generados.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
