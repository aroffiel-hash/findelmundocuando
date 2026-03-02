#!/usr/bin/env python3
"""
update_board.py
Llama a Groq API (Llama 3-70B) para regenerar data.json cada 12 horas.
GitHub Actions ejecuta este script y hace git push al repo.
"""

import os, json, sys, requests
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM = """Eres un analista de inteligencia geopolítica que actualiza un tablero de probabilidades.
Respondes ÚNICAMENTE con JSON válido. Sin markdown, sin explicaciones, sin bloques de código.
Usas cuotas americanas: -150 = favorito (60%), +200 = no favorito (33%).
"moved": "down" = cuota se ACORTÓ (más probable). "moved": "up" = cuota se ALARGÓ (menos probable). "moved": "none" = sin cambio."""

def prompt(today):
    return f"""Fecha actual: {today}

Genera un JSON actualizado para el tablero geopolítico "¿Fin del Mundo Cuándo?".
Usa noticias reales de hoy. Devuelve SOLO el JSON, sin ningún texto adicional.

Estructura EXACTA requerida:

{{
  "lastUpdated": "{today}",
  "ticker": [
    "⚡ Noticia urgente 1...",
    "🔴 Noticia urgente 2...",
    ... 15 a 18 items con emojis, en español, noticias reales del día
  ],
  "sections": [
    {{
      "flag": "🌍",
      "label": "ESCENARIOS MACRO",
      "rows": [
        {{"event": "El conflicto se mantiene solo regional", "odds": "-380", "params": "Análisis breve con fuente.", "moved": "none"}},
        {{"event": "3+ grandes potencias en conflicto directo en 2026", "odds": "+220", "params": "...", "moved": "down"}},
        {{"event": "WW3 activa en 4 frentes simultáneos", "odds": "+400", "params": "...", "moved": "none"}},
        {{"event": "Tercera Guerra Mundial por definición estricta", "odds": "+950", "params": "...", "moved": "none"}}
      ]
    }},
    {{"flag": "🇮🇷", "label": "IRÁN", "rows": [
      {{"event": "El gobierno iraní colapsa en 6 meses", "odds": "-160", "params": "...", "moved": "down"}},
      {{"event": "Irán se vuelve nuclear en 12 meses", "odds": "-180", "params": "...", "moved": "down"}},
      {{"event": "Muerte de Jamenei confirmada", "odds": "LIQUIDADO", "params": "✓ Confirmado TV estatal iraní, 28 feb 2026.", "moved": "none"}},
      {{"event": "Alto el fuego iraní en 30 días", "odds": "+1400", "params": "...", "moved": "up"}},
      {{"event": "Estrecho de Ormuz cerrado 30+ días", "odds": "+200", "params": "...", "moved": "up"}},
      {{"event": "Irán solicita asistencia militar del Talibán", "odds": "+130", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "🇲🇽", "label": "MÉXICO", "rows": [
      {{"event": "México sufre recesión técnica por shock del conflicto", "odds": "+220", "params": "...", "moved": "down"}},
      {{"event": "Peso mexicano cae 10%+ frente al dólar en 30 días", "odds": "+170", "params": "...", "moved": "down"}},
      {{"event": "Pemex sufre pérdidas extraordinarias o requiere rescate", "odds": "-120", "params": "...", "moved": "down"}},
      {{"event": "Sheinbaum convoca mediación de paz internacional", "odds": "+420", "params": "...", "moved": "none"}},
      {{"event": "Conflicto agrava crisis de seguridad interna en México", "odds": "-200", "params": "...", "moved": "down"}},
      {{"event": "México rompe relaciones con EE.UU. o Israel", "odds": "+1400", "params": "...", "moved": "none"}}
    ]}},
    {{"flag": "🇨🇺", "label": "CUBA", "rows": [
      {{"event": "Cuba sufre crisis energética severa por el conflicto", "odds": "-240", "params": "...", "moved": "down"}},
      {{"event": "Díaz-Canel participa en cumbre del eje anti-OTAN", "odds": "+160", "params": "...", "moved": "down"}},
      {{"event": "Cuba rompe relaciones con EE.UU. o expulsa embajadores", "odds": "+380", "params": "...", "moved": "down"}},
      {{"event": "EE.UU. toma acción coercitiva directa contra Cuba", "odds": "+520", "params": "...", "moved": "up"}},
      {{"event": "Cuba formaliza alianza de defensa con Irán", "odds": "+950", "params": "...", "moved": "none"}}
    ]}},
    {{"flag": "🇺🇦", "label": "UCRANIA", "rows": [
      {{"event": "Zelenski presiona por más armamento por el contexto iraní", "odds": "-500", "params": "...", "moved": "down"}},
      {{"event": "Ucrania recibe menos ayuda por distracción del Congreso", "odds": "-160", "params": "...", "moved": "down"}},
      {{"event": "Rusia aprovecha distracción de EE.UU. para avanzar", "odds": "+140", "params": "...", "moved": "down"}},
      {{"event": "Zelenski acepta armas nucleares de aliado occidental", "odds": "+280", "params": "...", "moved": "down"}},
      {{"event": "Rusia-Ucrania logran alto el fuego mediado por Trump", "odds": "+320", "params": "...", "moved": "up"}}
    ]}},
    {{"flag": "🇹🇼", "label": "TAIWÁN", "rows": [
      {{"event": "China lanza ejercicios militares a gran escala en 30 días", "odds": "-200", "params": "...", "moved": "down"}},
      {{"event": "Trump hace concesiones sobre Taiwán a cambio de neutralidad china", "odds": "+200", "params": "...", "moved": "down"}},
      {{"event": "China intenta bloqueo o acción militar en 60 días", "odds": "+350", "params": "...", "moved": "down"}},
      {{"event": "China actúa militarmente contra Taiwán en 12 meses", "odds": "+165", "params": "...", "moved": "down"}},
      {{"event": "Taiwán activa reservistas y acelera compras de armamento", "odds": "-180", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "🇦🇫", "label": "AFGANISTÁN / ALIANZA IRANÍ", "rows": [
      {{"event": "Talibán proporciona apoyo material a Irán", "odds": "+190", "params": "...", "moved": "down"}},
      {{"event": "Talibán abre frente oriental contra Pakistán", "odds": "+420", "params": "...", "moved": "up"}},
      {{"event": "Alianza militar formal Talibán-Irán", "odds": "+480", "params": "...", "moved": "none"}}
    ]}},
    {{"flag": "🇵🇰", "label": "PAKISTÁN", "rows": [
      {{"event": "Conflicto Pak-Afg se expande significativamente", "odds": "-115", "params": "...", "moved": "up"}},
      {{"event": "Pakistán utiliza arma nuclear", "odds": "+750", "params": "...", "moved": "down"}},
      {{"event": "Golpe de estado o desestabilización del gobierno", "odds": "+280", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "🇨🇳", "label": "CHINA", "rows": [
      {{"event": "China provee ayuda militar directa a Irán", "odds": "+460", "params": "...", "moved": "up"}},
      {{"event": "China entra en conflicto directo con EE.UU.", "odds": "+580", "params": "...", "moved": "up"}}
    ]}},
    {{"flag": "🇷🇺", "label": "RUSIA", "rows": [
      {{"event": "Rusia lanza ofensiva mayor en Ucrania", "odds": "+140", "params": "...", "moved": "down"}},
      {{"event": "Rusia establece alianza formal con Irán", "odds": "+230", "params": "...", "moved": "down"}},
      {{"event": "Rusia entra en conflicto con miembro de la OTAN", "odds": "+520", "params": "...", "moved": "none"}}
    ]}},
    {{"flag": "🇰🇵", "label": "COREA DEL NORTE", "rows": [
      {{"event": "Prueba nuclear o de ICBM en 30 días", "odds": "-160", "params": "...", "moved": "down"}},
      {{"event": "Provocaciones de artillería o fronterizas escalan", "odds": "-240", "params": "...", "moved": "down"}},
      {{"event": "Invasión total de Corea del Sur", "odds": "+360", "params": "...", "moved": "down"}},
      {{"event": "Transfiere armas o tropas al conflicto iraní", "odds": "+195", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "🇺🇸", "label": "EE.UU. — INTERIOR", "rows": [
      {{"event": "Órdenes stop-loss activadas por el Pentágono", "odds": "-500", "params": "...", "moved": "down"}},
      {{"event": "Activación plena de la Guardia Nacional o Reserva", "odds": "-320", "params": "...", "moved": "down"}},
      {{"event": "Se reinstala el reclutamiento militar obligatorio", "odds": "+210", "params": "...", "moved": "down"}},
      {{"event": "Declaración de guerra formal del Congreso", "odds": "+260", "params": "...", "moved": "down"}},
      {{"event": "Poderes de Guerra llega al Tribunal Supremo", "odds": "-220", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "💰", "label": "ECONOMÍA", "rows": [
      {{"event": "Petróleo Brent por encima de $100 en 7 días", "odds": "-140", "params": "...", "moved": "down"}},
      {{"event": "Petróleo WTI por encima de $150 en 90 días", "odds": "+140", "params": "...", "moved": "down"}},
      {{"event": "Recesión global declarada por el FMI", "odds": "+140", "params": "...", "moved": "down"}},
      {{"event": "S&P 500 cae 20%+ en 90 días", "odds": "+160", "params": "...", "moved": "down"}},
      {{"event": "OPEC+ acelera producción de emergencia", "odds": "-160", "params": "...", "moved": "down"}}
    ]}},
    {{"flag": "🎲", "label": "LONGSHOTS", "rows": [
      {{"event": "ONU aprueba resolución vinculante de alto el fuego", "odds": "+2500", "params": "...", "moved": "up"}},
      {{"event": "Alto el fuego simultáneo en todos los frentes", "odds": "+1800", "params": "...", "moved": "up"}},
      {{"event": "Una arma nuclear utilizada en cualquier lugar", "odds": "+420", "params": "...", "moved": "down"}},
      {{"event": "Dos o más armas nucleares utilizadas", "odds": "+950", "params": "...", "moved": "down"}},
      {{"event": "WW3 por todas las definiciones antes del 31 dic 2026", "odds": "+1500", "params": "...", "moved": "down"}}
    ]}}
  ],
  "newsCards": [
    {{"tag": "TEHERÁN", "tagColor": "#7B1D1D", "headline": "Titular de la noticia principal", "sub": "Subtítulo con fuente y datos. Agencia, fecha.", "credit": "Reuters · AP", "wikiTitle": "Tehran", "icon": "💥"}},
    {{"tag": "WANG YI — BEIJING", "tagColor": "#C00000", "headline": "Wang Yi: declaración clave del día", "sub": "Contexto breve.", "credit": "Xinhua", "wikiTitle": "Wang Yi (politician)", "icon": "🇨🇳"}},
    {{"tag": "VLADÍMIR PUTIN", "tagColor": "#1A3A8B", "headline": "Putin: declaración o acción del día", "sub": "Contexto.", "credit": "TASS", "wikiTitle": "Vladimir Putin", "icon": "🇷🇺"}},
    {{"tag": "ESTRECHO DE ORMUZ", "tagColor": "#004E6B", "headline": "Situación en Ormuz hoy", "sub": "Datos de tráfico y precios.", "credit": "S&P Global", "wikiTitle": "Strait of Hormuz", "icon": "🛢️"}},
    {{"tag": "NARENDRA MODI", "tagColor": "#FF6600", "headline": "India: postura diplomática del día", "sub": "Contexto.", "credit": "NDTV", "wikiTitle": "Narendra Modi", "icon": "🇮🇳"}},
    {{"tag": "WILLIAM LAI — TAIWÁN", "tagColor": "#00486B", "headline": "Taiwán: declaración o movimiento del día", "sub": "Contexto.", "credit": "Reuters", "wikiTitle": "William Lai", "icon": "🇹🇼"}},
    {{"tag": "CONSEJO DE SEGURIDAD ONU", "tagColor": "#1B5E38", "headline": "ONU: situación del día", "sub": "Contexto.", "credit": "UN News", "wikiTitle": "United Nations Security Council", "icon": "🏛️"}},
    {{"tag": "KARACHI — PAKISTÁN", "tagColor": "#3A6B1B", "headline": "Pakistán: situación del día", "sub": "Contexto.", "credit": "Dawn News", "wikiTitle": "Karachi", "icon": "🇵🇰"}}
  ],
  "breakingNews": [
    {{"icon": "💀", "text": "Noticia de última hora 1"}},
    {{"icon": "🛳️", "text": "Noticia de última hora 2"}},
    {{"icon": "⛽", "text": "Noticia de última hora 3"}},
    {{"icon": "🕊️", "text": "Noticia de última hora 4"}},
    {{"icon": "🇹🇼", "text": "Noticia de última hora 5"}}
  ],
  "keyOdds": [
    {{"label": "Irán nuclear / 12m", "odds": "-180", "pct": 64}},
    {{"label": "WW3 definición estricta", "odds": "+950", "pct": 10}},
    {{"label": "OPEC+ acelera producción", "odds": "-160", "pct": 62}},
    {{"label": "Arma nuclear utilizada", "odds": "+420", "pct": 19}},
    {{"label": "Taiwán activada / 60d", "odds": "-180", "pct": 64}}
  ],
  "methodology": "Síntesis analítica especulativa basada en fuentes abiertas: CFR, RAND, CSER, S&P Global, CENTCOM, medios verificados. Las cuotas no son apuestas reales.",
  "sources": [
    {{"name": "CNN en Español", "description": "Cobertura en vivo del conflicto.", "url": "https://cnnespanol.cnn.com"}},
    {{"name": "S&P Global", "description": "Datos de tráfico de Ormuz y energía.", "url": "https://www.spglobal.com"}},
    {{"name": "CENTCOM", "description": "Comunicados militares oficiales EE.UU.", "url": "https://www.centcom.mil"}},
    {{"name": "Infobae", "description": "Cobertura en tiempo real.", "url": "https://www.infobae.com"}}
  ]
}}

REGLAS CRÍTICAS:
1. Mantén EXACTAMENTE las 14 secciones en ese orden con esos labels y flags.
2. Reemplaza TODOS los "..." con análisis real y conciso del día de hoy ({today}).
3. Ajusta las odds según noticias reales — si hay escalada, acorta favoritos; si hay desescalada, alarga.
4. newsCards.wikiTitle DEBE ser un título exacto de artículo en Wikipedia en inglés (para búsqueda de imagen).
5. Todo el texto en español excepto wikiTitle.
6. Devuelve ÚNICAMENTE el JSON. Sin markdown, sin explicaciones."""

def run():
    if not GROQ_API_KEY:
        print("ERROR: falta GROQ_API_KEY")
        sys.exit(1)

    today = datetime.utcnow().strftime("%-d de %B de %Y")
    print(f"[{datetime.utcnow().isoformat()}] Generando data.json · {today}")

    r = requests.post(GROQ_URL,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user",   "content": prompt(today)},
            ],
            "temperature": 0.25,
            "max_tokens": 8000,
            "response_format": {"type": "json_object"},
        },
        timeout=90
    )
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]

    # Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # Try to clean common issues
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data = json.loads(clean)

    # Sanity checks
    assert "sections" in data and len(data["sections"]) >= 14, f"Faltan secciones: {len(data.get('sections',[]))}"
    assert "ticker" in data and len(data["ticker"]) >= 5, "Ticker vacío"

    # Ensure lastUpdated is set
    data["lastUpdated"] = datetime.utcnow().strftime("%-d de %B de %Y — %H:%M UTC")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_rows = sum(len(s.get("rows", s.get("items", []))) for s in data["sections"])
    cards = len(data.get("newsCards", []))
    print(f"  ✓ Guardado: {len(data['sections'])} secciones · {total_rows} apuestas · {cards} news cards")
    print(f"  ✓ Última actualización: {data['lastUpdated']}")

if __name__ == "__main__":
    run()
