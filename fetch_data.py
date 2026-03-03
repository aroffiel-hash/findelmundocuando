import json
import urllib.request
from datetime import datetime
import xml.etree.ElementTree as ET

# ── SECCIONES ─────────────────────────────────────────────────────────────────
SECTIONS_DEF = [
    {
        "flag": "🌍",
        "label": "GEOPOLÍTICA Y CONFLICTO",
        "keywords": [
            "war", "military", "missile", "russia", "ukraine", "israel", "iran",
            "gaza", "taiwan", "china", "korea", "nato", "troops", "airstrike",
            "nuclear", "attack", "combat", "conflict", "ceasefire", "escalat",
            "hostage", "crimea", "sanctions", "invasion", "siege", "bomb",
        ],
    },
    {
        "flag": "💰",
        "label": "ECONOMÍA Y RECURSOS",
        "keywords": [
            "oil", "gas", "fed", "interest rate", "inflation", "economy", "brent",
            "gdp", "recession", "opec", "currency", "trade war", "tariff",
            "debt ceiling", "dow jones", "s&p 500", "bond", "yield",
        ],
    },
    {
        "flag": "🏛️",
        "label": "POLÍTICA INTERNACIONAL",
        "keywords": [
            "president", "election", "prime minister", "minister", "senate",
            "congress", "government", "treaty", "summit", "diplomatic",
            "impeach", "resign", "vote", "poll", "approval rating",
        ],
    },
    {
        "flag": "🌐",
        "label": "ESCENARIOS GLOBALES",
        "keywords": [""],  # Fallback
    },
]

# Exclusiones — deportes, entretenimiento, crypto especulativo
EXCLUDE_KEYWORDS = [
    "nba", "nfl", "nhl", "mlb", "fifa", "soccer", "football score",
    "tennis", "ufc", "boxing", "wrestling", "golf", "f1 race",
    "stanley cup", "super bowl", "world cup", "champions league",
    "oscar", "grammy", "emmy", "tony award", "celebrity",
    "taylor swift", "rihanna", "beyoncé", "drake", "kanye",
    "bitcoin", "ethereum", "dogecoin", "solana", "crypto price",
    "nft", "defi", "altcoin", "gta vi", "before gta",
    "kardashian", "pope", "jesus christ", "alien",
    "tiktok creator", "streaming", "movie box office",
    "microstrategy", "kraken ipo", "bitboy",
]

# Categorías de exclusión para el FALLBACK (ESCENARIOS GLOBALES)
# — evita que termine lleno de deportes
FALLBACK_EXCLUDE = [
    "set 1", "game 1", "match", "o/u", "spread:", "moneyline",
    "set games", "1st quarter", "3rd quarter", "overtime",
    "winner: ",
]


def is_relevant(title: str) -> bool:
    low = title.lower()
    return not any(kw in low for kw in EXCLUDE_KEYWORDS)


def is_fallback_ok(title: str) -> bool:
    low = title.lower()
    return not any(kw in low for kw in FALLBACK_EXCLUDE)


def fetch_ticker_news():
    """Titulares de Al Jazeera para el ticker."""
    try:
        url = "https://www.aljazeera.com/xml/rss/all.xml"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=10).read()
        root = ET.fromstring(response)
        items = root.findall(".//item")
        headlines = []
        for item in items[:15]:
            t = item.find("title")
            if t is not None and t.text:
                headlines.append(t.text.strip())
        return headlines if headlines else ["Sincronizando noticias..."]
    except Exception as e:
        print(f"[ticker] Error: {e}")
        return ["Error conectando a red de noticias"]


def get_prob(market: dict) -> float | None:
    """
    Extrae la probabilidad real de un mercado de Polymarket.
    Prioriza lastTradePrice (precio de la última transacción real),
    como fallback usa outcomePrices[0].
    Retorna None si el mercado está resuelto o no tiene precio válido.
    """
    # lastTradePrice es el precio más reciente de mercado real
    ltp = market.get("lastTradePrice")
    try:
        if ltp is not None:
            p = float(ltp)
            if 0.03 <= p <= 0.97:
                return p
    except (TypeError, ValueError):
        pass

    # Fallback: outcomePrices[0]
    op = market.get("outcomePrices", [])
    try:
        if op:
            p = float(op[0])
            if 0.03 <= p <= 0.97:
                return p
    except (TypeError, ValueError, IndexError):
        pass

    return None  # Mercado resuelto o sin precio real


def prob_to_odds(prob: float) -> str:
    """Convierte probabilidad decimal a momio americano string."""
    p = min(max(prob, 0.0001), 0.9999)
    if p > 0.5:
        return str(int(-(p / (1 - p)) * 100))   # Ej: "-200"
    else:
        return f"+{int(((1 - p) / p) * 100)}"   # Ej: "+300"


def fetch_polymarket_odds():
    """
    Consulta los 500 mercados más activos de Polymarket ordenados por volumen.
    Usa lastTradePrice como probabilidad real.
    """
    url = (
        "https://gamma-api.polymarket.com/markets"
        "?active=true&closed=false&limit=500&order=volume&ascending=false"
    )

    sections = [{**s, "rows": []} for s in SECTIONS_DEF]
    placed_titles = set()  # Evitar duplicados

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        response = urllib.request.urlopen(req, timeout=20)
        markets = json.loads(response.read())

        for market in markets:
            title = (market.get("question") or market.get("title") or "").strip()
            if not title or title in placed_titles:
                continue
            if not is_relevant(title):
                continue

            prob = get_prob(market)
            if prob is None:
                continue

            odds_str = prob_to_odds(prob)

            row = {
                "event": title,
                "odds": odds_str,
                "params": "Fuente: Polymarket",
                "moved": "none",
            }

            # Clasificar en sección
            placed = False
            for sec in sections[:-1]:
                if any(kw in title.lower() for kw in sec["keywords"] if kw):
                    if len(sec["rows"]) < 7:
                        sec["rows"].append(row)
                        placed_titles.add(title)
                    placed = True
                    break

            if not placed and is_fallback_ok(title) and len(sections[-1]["rows"]) < 8:
                sections[-1]["rows"].append(row)
                placed_titles.add(title)

        # Construir output
        final = []
        for sec in sections:
            if sec["rows"]:
                final.append({"flag": sec["flag"], "label": sec["label"], "rows": sec["rows"]})
        return final

    except Exception as e:
        print(f"[polymarket] Error: {e}")
        return [{
            "flag": "⚠️",
            "label": "ERROR",
            "rows": [{"event": f"No se pudieron obtener datos: {e}", "odds": "N/A", "params": "", "moved": "none"}],
        }]


if __name__ == "__main__":
    now = datetime.utcnow()
    meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ts = now.strftime(f"%d de {meses[now.month]} de %Y — %H:%M UTC")

    print("Obteniendo noticias del ticker...")
    ticker = fetch_ticker_news()

    print("Obteniendo momios de Polymarket...")
    sections = fetch_polymarket_odds()

    output = {"lastUpdated": ts, "ticker": ticker, "sections": sections}

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(s["rows"]) for s in sections)
    print(f"✅ data.json generado: {len(sections)} secciones, {total} eventos.")
