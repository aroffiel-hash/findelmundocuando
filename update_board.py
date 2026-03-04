"""
fetch_data.py — Fallback sin clave de Groq.
Extrae solo mercados estrictamente geopolíticos de Polymarket.
Usa whitelist pura: si no matchea, se descarta sin excepción.
"""
import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

# ── WHITELIST GEOPOLÍTICA (si no aparece ninguna → RECHAZAR) ──────────────────
GEO_WHITELIST = [
    # Conflictos activos
    "iran","israel","gaza","hamas","hezbollah","houthi","irgc",
    "ukraine","russia","zelensky","putin","nato","crimea","donbas",
    "taiwan","china","xi jinping","south china sea","north korea","kim jong",
    "pakistan","afghanistan","taliban","kashmir",
    # EE.UU. geopolítica
    "trump","congress","senate","pentagon","military operations","war with",
    "tariff","sanctions","us troops","us military","us embassy",
    # Actores y lugares clave
    "hormuz","strait","gulf state","saudi","emirates","qatar","oman","turkey",
    "jerusalem","west bank","beirut","tehran","kyiv","moscow","beijing",
    # Términos de conflicto
    "nuclear","airstrike","missile","ceasefire","invasion","coup","escalat",
    "warship","drone attack","ballistic","weapon","troops deploy",
    # Economía geopolítica
    "oil price","crude oil","opec","brent","gas price",
    "recession","interest rate","federal reserve","eurozone gdp",
    "fed decrease","fed increase","fed rate","tariff bill",
]

# ── BLOCKLIST ABSOLUTA (si aparece alguna → RECHAZAR siempre) ─────────────────
HARD_BLOCK = [
    # Deportes — equipos y ligas
    " vs ", " vs.", "senators","flames","knights","golden knights","leafs",
    "maple leafs","canucks","oilers","bruins","rangers","penguins","capitals",
    "lakers","celtics","warriors","bulls","heat","nets","bucks","nuggets",
    "chiefs","eagles","cowboys","patriots","packers","niners","bears",
    "yankees","dodgers","astros","braves","mets","cubs","sox",
    "arsenal","chelsea","liverpool","manchester","barcelona","madrid","genoa",
    "roma as","ac milan","juventus","inter milan","breda","perth glory",
    "nac breda","brighton","atlanta united","la galaxy","seattle sounders",
    "pine bluff","jackson state","arkansas",
    # Ligas y competencias deportivas
    "nba","nfl","nhl","mlb","mls","ufc","wwe","pga tour","f1 race",
    "super bowl","stanley cup","world series","champions league","europa league",
    "copa del rey","fa cup","premier league","la liga","serie a","bundesliga",
    "ligue 1","playoff","draft pick","trade deadline","free agent",
    # Entretenimiento completo
    "oscar","academy award","golden globe","emmy","grammy","bafta","tony award",
    "sinners","bridgerton","stranger things","squid game","the bear",
    "taylor swift","beyoncé","rihanna","drake","kanye","ariana",
    "box office","film gross","movie gross","streaming views",
    "reality show","fashion week","album release","concert tour","tour dates",
    # Noticias triviales
    "temperature in","degrees celsius","degrees fahrenheit","weather",
    "tweets in","tweet count","post count","elon musk tweet","musk post",
    "followers","engagement","viral","trending",
    "posy li","bridgerton","engaged in","wedding in",
    "bitcoin price","ethereum price","crypto price","dogecoin","solana",
    "nft ","defi ","altcoin",
    # Política electoral menor
    "nominee for senate in","democratic nominee for","republican nominee for",
    "guinea-bissau","jared hudson","saxon callahan","jack reed rhode island",
    "poilievre","conservative leader","prime minister of the uk",
]

def passes_whitelist(title: str) -> bool:
    """True solo si el evento tiene keyword geopolítica positiva."""
    low = title.lower()
    return any(kw in low for kw in GEO_WHITELIST)

def passes_blocklist(title: str) -> bool:
    """True si NO hay ningún término bloqueado."""
    low = title.lower()
    return not any(kw in low for kw in HARD_BLOCK)

def is_valid(title: str) -> bool:
    return passes_blocklist(title) and passes_whitelist(title)

# ── SECCIONES con keywords específicas ───────────────────────────────────────
SECTIONS_DEF = [
    {
        "flag": "☢️", "label": "IRÁN Y ORIENTE MEDIO",
        "keywords": ["iran","israel","gaza","hamas","hezbollah","houthi","irgc",
                     "hormuz","gulf","beirut","tehran","arab state","saudi","qatar"],
    },
    {
        "flag": "🇷🇺", "label": "RUSIA / UCRANIA / OTAN",
        "keywords": ["russia","ukraine","nato","zelensky","putin","kyiv","moscow",
                     "crimea","donbas","otan","soviet"],
    },
    {
        "flag": "🇨🇳", "label": "CHINA / PACÍFICO / COREA",
        "keywords": ["china","taiwan","xi jinping","beijing","south china sea",
                     "north korea","kim jong","japan","philippines","semiconductor"],
    },
    {
        "flag": "🇺🇸", "label": "EE.UU. — GEOPOLÍTICA",
        "keywords": ["trump","pentagon","military operations","war with iran","us troops",
                     "us military","us embassy","tariff","sanctions","us congress","senate vote"],
    },
    {
        "flag": "💰", "label": "ECONOMÍA Y ENERGÍA",
        "keywords": ["oil price","crude oil","opec","brent","gas price",
                     "recession","interest rate","federal reserve","eurozone gdp",
                     "fed decrease","fed rate","tariff bill","inflation"],
    },
    {
        "flag": "🌍", "label": "ESCENARIOS GEOPOLÍTICOS",
        "keywords": [""],  # Fallback — solo llega aquí si pasó whitelist
    },
]

PARAMS_ES = {
    "iran":       "Probabilidad según mercado activo. Escenario iraní en desarrollo.",
    "israel":     "Probabilidad según mercado activo. Relacionado con conflicto en Medio Oriente.",
    "ukraine":    "Probabilidad según mercado activo. Relacionado con conflicto Rusia-Ucrania.",
    "russia":     "Probabilidad según mercado activo. Escenario ruso en evolución.",
    "taiwan":     "Probabilidad según mercado activo. Relacionado con tensión China-Taiwán.",
    "china":      "Probabilidad según mercado activo. Escenario China en curso.",
    "north korea":"Probabilidad según mercado activo. Escenario peninsular coreano.",
    "tariff":     "Probabilidad según mercado activo. Relacionado con política arancelaria de EE.UU.",
    "oil":        "Probabilidad según mercado activo. Relacionado con precio del petróleo.",
    "recession":  "Probabilidad según mercado activo. Escenario de recesión económica.",
    "nato":       "Probabilidad según mercado activo. Escenario OTAN en desarrollo.",
    "nuclear":    "Probabilidad según mercado activo. Escenario de riesgo nuclear.",
    "fed ":       "Probabilidad según mercado activo. Relacionado con política monetaria de la Fed.",
    "trump":      "Probabilidad según mercado activo. Decisión de la administración Trump.",
    "zelensky":   "Probabilidad según mercado activo. Relacionado con liderazgo ucraniano.",
    "sanctions":  "Probabilidad según mercado activo. Relacionado con sanciones internacionales.",
}

def make_params(title: str, prob_pct: int) -> str:
    low = title.lower()
    nivel = "Alta" if prob_pct >= 60 else ("Moderada" if prob_pct >= 30 else "Baja")
    for kw, desc in PARAMS_ES.items():
        if kw in low:
            return f"{nivel} probabilidad en mercado activo. {desc}"
    return f"{nivel} probabilidad según mercado de predicción activo. Escenario geopolítico en curso."

def get_prob(market: dict):
    for field in ["lastTradePrice", "outcomePrices"]:
        val = market.get(field)
        try:
            p = float(val[0] if isinstance(val, list) else val)
            if 0.03 <= p <= 0.97:
                return p
        except (TypeError, ValueError, IndexError):
            pass
    return None

def prob_to_odds(p: float) -> str:
    p = min(max(p, 0.0001), 0.9999)
    return str(int(-(p / (1-p)) * 100)) if p > 0.5 else f"+{int(((1-p)/p) * 100)}"

def get_section_idx(title: str) -> int:
    low = title.lower()
    for i, sec in enumerate(SECTIONS_DEF[:-1]):
        if any(kw in low for kw in sec["keywords"] if kw):
            return i
    return len(SECTIONS_DEF) - 1  # fallback geopolítico

def fetch_ticker_news():
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        root = ET.fromstring(urllib.request.urlopen(req, timeout=10).read())
        headlines = []
        for item in root.findall(".//item"):
            t = item.find("title")
            if t is not None and t.text:
                txt = t.text.strip()
                if passes_blocklist(txt):  # Solo titulares no deportivos
                    headlines.append(txt)
            if len(headlines) >= 12:
                break
        return headlines or ["Sincronizando noticias geopolíticas..."]
    except Exception as e:
        return [f"Error: {e}"]

def fetch_polymarket_odds():
    url = ("https://gamma-api.polymarket.com/markets"
           "?active=true&closed=false&limit=600&order=volume&ascending=false")
    sections = [{**s, "rows": []} for s in SECTIONS_DEF]
    placed = set()
    accepted = 0
    rejected = 0

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        markets = json.loads(urllib.request.urlopen(req, timeout=20).read())

        for m in markets:
            title = (m.get("question") or m.get("title") or "").strip()
            if not title or title in placed:
                continue

            if not is_valid(title):
                rejected += 1
                continue

            prob = get_prob(m)
            if prob is None:
                continue

            si = get_section_idx(title)
            sec = sections[si]
            if len(sec["rows"]) >= 8:
                continue

            sec["rows"].append({
                "event":  title,
                "odds":   prob_to_odds(prob),
                "params": make_params(title, round(prob * 100)),
                "moved":  "none",
            })
            placed.add(title)
            accepted += 1

        print(f"  Aceptados: {accepted} | Rechazados: {rejected}")
        return [{"flag": s["flag"], "label": s["label"], "rows": s["rows"]}
                for s in sections if s["rows"]]

    except Exception as e:
        print(f"[polymarket] Error: {e}")
        return [{"flag": "⚠️", "label": "ERROR",
                 "rows": [{"event": str(e), "odds": "N/A", "params": "", "moved": "none"}]}]


if __name__ == "__main__":
    now = datetime.utcnow()
    meses = ["","enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    ts = now.strftime(f"%d de {meses[now.month]} de %Y — %H:%M UTC")

    print("Obteniendo ticker de Al Jazeera...")
    ticker = fetch_ticker_news()

    print("Obteniendo mercados geopolíticos de Polymarket...")
    sections = fetch_polymarket_odds()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump({"lastUpdated": ts, "ticker": ticker, "sections": sections},
                  f, ensure_ascii=False, indent=2)

    total = sum(len(s["rows"]) for s in sections)
    print(f"data.json: {len(sections)} secciones, {total} eventos.")
