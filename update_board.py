import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

# ── EXCLUSIONES ESTRICTAS ─────────────────────────────────────────────────────
# Estas palabras en el título = descartar sin importar la sección
EXCLUDE_HARD = [
    # Deportes
    "nba ","nfl ","nhl ","mlb ","mls ","fifa","soccer","football score",
    "stanley cup","super bowl","world cup","champions league","premier league",
    "la liga","serie a","bundesliga","ligue 1","copa del rey","fa cup",
    "cricket","tennis","ufc","boxing","wrestling","golf","f1 race","formula 1",
    "vs.", " vs ", "match ", "game ", "draw ", "win on ", "win the ",
    "o/u ", "spread:", "moneyline","1st quarter","3rd quarter","overtime",
    "both teams to score","set 1","set games","winner: ",
    # Entretenimiento
    "oscar","grammy","emmy","tony award","golden globe","bafta",
    "celebrity","kardashian","taylor swift","beyoncé","rihanna","drake",
    "box office","movie gross","film festival","streaming","album release",
    "concert tour","reality show","bridgerton","sinners",
    # Crypto especulativo
    "bitcoin price","ethereum price","dogecoin","solana price",
    "nft ","defi ","altcoin","microstrategy","kraken ipo",
    # Misc
    "gta vi","pope francis","jesus christ","alien",
]

# Palabras que CONFIRMAN contenido geopolítico relevante
GEO_POSITIVE = [
    "war","military","missile","russia","ukraine","israel","iran","gaza",
    "taiwan","china","korea","nato","troops","airstrike","nuclear","attack",
    "conflict","ceasefire","sanction","invasion","bomb","coup","protest",
    "election","president","minister","government","treaty","diplomatic",
    "oil","gas","inflation","recession","tariff","trade","economic",
    "refugee","crisis","terror","cartel","mexico","pakistan","afghanistan",
    "hezbollah","irgc","hamas","houthi","pentagon","kremlin","white house",
    "congress","un security","un council","senate","parliament",
    "north korea","south china","strait","strait of hormuz",
    "trump","biden","zelensky","netanyahu","khamenei","xi jinping","putin",
    "escalat","ceasefire","negotiat","sanction","missile",
]

# Mapa de secciones con keywords específicas
SECTIONS_DEF = [
    {
        "flag": "☢️",
        "label": "ORIENTE MEDIO Y CONFLICTO",
        "keywords": [
            "iran","israel","gaza","hamas","hezbollah","houthi","irgc",
            "hormuz","gulf","beirut","tehran","middle east","arab",
            "airstrike","strike on","attack on","war with",
        ],
    },
    {
        "flag": "🇷🇺",
        "label": "RUSIA / UCRANIA / OTAN",
        "keywords": [
            "russia","ukraine","nato","kremlin","zelensky","putin",
            "kyiv","moscow","crimea","donbas","otan","soviet",
        ],
    },
    {
        "flag": "🇨🇳",
        "label": "CHINA / ASIA PACIFIC",
        "keywords": [
            "china","taiwan","xi jinping","beijing","hong kong",
            "south china sea","north korea","kim jong","indo-pacific",
            "japan","south korea","philippines","semiconductor",
        ],
    },
    {
        "flag": "🇺🇸",
        "label": "EE.UU. — POLÍTICA Y ECONOMÍA",
        "keywords": [
            "trump","congress","senate","white house","pentagon",
            "tariff","fed ","federal reserve","us economy","us military",
            "midterm","republican","democrat","election",
        ],
    },
    {
        "flag": "💰",
        "label": "ECONOMÍA Y ENERGÍA GLOBAL",
        "keywords": [
            "oil price","crude","opec","gas price","brent","inflation",
            "recession","gdp","interest rate","bond yield","stock market",
            "trade war","supply chain","energy","eurozone",
        ],
    },
    {
        "flag": "🌍",
        "label": "ESCENARIOS GEOPOLÍTICOS",
        "keywords": [""],  # fallback — solo geopolítico confirmado
    },
]

# Traducciones de términos comunes inglés → español para los params
TERM_TRANSLATIONS = {
    "military operations": "operaciones militares",
    "ceasefire": "alto el fuego",
    "nuclear": "nuclear",
    "invasion": "invasión",
    "election": "elección",
    "president": "presidente",
    "congress": "congreso",
    "tariff": "arancel",
    "oil price": "precio del petróleo",
    "recession": "recesión",
    "interest rate": "tasa de interés",
    "sanctions": "sanciones",
    "troops": "tropas",
    "airstrike": "ataque aéreo",
    "prime minister": "primer ministro",
    "government": "gobierno",
    "treaty": "tratado",
}

def is_blocked(title: str) -> bool:
    low = title.lower()
    return any(kw in low for kw in EXCLUDE_HARD)

def is_geopolitical(title: str) -> bool:
    low = title.lower()
    return any(kw in low for kw in GEO_POSITIVE)

def get_section(title: str) -> int:
    """Retorna índice de sección (0-5). -1 si no aplica."""
    low = title.lower()
    for i, sec in enumerate(SECTIONS_DEF[:-1]):
        if any(kw in low for kw in sec["keywords"] if kw):
            return i
    if is_geopolitical(title):
        return len(SECTIONS_DEF) - 1  # fallback geopolítico
    return -1

def make_params_es(title: str, prob_pct: int) -> str:
    """Genera params descriptivos en español basados en el título."""
    low = title.lower()
    prefix = "Alta probabilidad" if prob_pct >= 60 else ("Probabilidad moderada" if prob_pct >= 30 else "Baja probabilidad")
    # Término dominante
    for en, es in TERM_TRANSLATIONS.items():
        if en in low:
            return f"{prefix} según mercados de predicción. Escenario relacionado con {es}. Dato de mercado activo."
    return f"{prefix} según mercados de predicción. Fuente: datos de mercado en tiempo real."

def get_prob(market: dict):
    ltp = market.get("lastTradePrice")
    try:
        if ltp is not None:
            p = float(ltp)
            if 0.03 <= p <= 0.97:
                return p
    except (TypeError, ValueError):
        pass
    op = market.get("outcomePrices", [])
    try:
        if op:
            p = float(op[0])
            if 0.03 <= p <= 0.97:
                return p
    except (TypeError, ValueError, IndexError):
        pass
    return None

def prob_to_odds(prob: float) -> str:
    p = min(max(prob, 0.0001), 0.9999)
    if p > 0.5:
        return str(int(-(p / (1 - p)) * 100))
    else:
        return f"+{int(((1 - p) / p) * 100)}"

def fetch_ticker_news():
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=10).read()
        root = ET.fromstring(response)
        items = root.findall(".//item")
        headlines = []
        for item in items[:20]:
            t = item.find("title")
            if t is not None and t.text and not is_blocked(t.text):
                headlines.append(t.text.strip())
            if len(headlines) >= 12:
                break
        return headlines if headlines else ["Sincronizando noticias geopolíticas..."]
    except Exception as e:
        print(f"[ticker] Error: {e}")
        return ["Error conectando a red de noticias"]

def fetch_polymarket_odds():
    url = (
        "https://gamma-api.polymarket.com/markets"
        "?active=true&closed=false&limit=600&order=volume&ascending=false"
    )
    sections = [{**s, "rows": []} for s in SECTIONS_DEF]
    placed_titles = set()

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=20)
        markets = json.loads(response.read())

        for market in markets:
            title = (market.get("question") or market.get("title") or "").strip()
            if not title or title in placed_titles:
                continue
            if is_blocked(title):
                continue

            sec_idx = get_section(title)
            if sec_idx < 0:
                continue  # No es geopolítico — descartar

            prob = get_prob(market)
            if prob is None:
                continue

            odds_str = prob_to_odds(prob)
            prob_pct  = round(prob * 100)

            row = {
                "event":  title,
                "odds":   odds_str,
                "params": make_params_es(title, prob_pct),
                "moved":  "none",
            }

            sec = sections[sec_idx]
            if len(sec["rows"]) < 8:
                sec["rows"].append(row)
                placed_titles.add(title)

        final = []
        for sec in sections:
            if sec["rows"]:
                final.append({"flag": sec["flag"], "label": sec["label"], "rows": sec["rows"]})
        return final

    except Exception as e:
        print(f"[polymarket] Error: {e}")
        return [{"flag": "⚠️", "label": "ERROR", "rows": [{"event": f"Error: {e}", "odds": "N/A", "params": "", "moved": "none"}]}]


if __name__ == "__main__":
    now = datetime.utcnow()
    meses = ["","enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
    ts = now.strftime(f"%d de {meses[now.month]} de %Y — %H:%M UTC")

    print("Obteniendo noticias del ticker...")
    ticker = fetch_ticker_news()

    print("Obteniendo datos de Polymarket (solo contenido geopolítico)...")
    sections = fetch_polymarket_odds()

    output = {"lastUpdated": ts, "ticker": ticker, "sections": sections}

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(s["rows"]) for s in sections)
    print(f"data.json generado: {len(sections)} secciones, {total} eventos.")
