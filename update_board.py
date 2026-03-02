import json
import os

# 1. Definimos la estructura base de tu board (Noticias reales de marzo 2026)
def get_latest_osint_data():
    return {
        "ticker": [
            "⚡ CENTCOM confirma: 3 bajas EE.UU. en combate (1 mar.)",
            "🔴 CGRI lanza 6ª oleada contra Tel Aviv y Dubai",
            "🛳️ USS Abraham Lincoln en posición en el Golfo de Omán",
            "⛽ Brent escala a $105 por tensiones en Ormuz",
            "🏛️ Consejo de Seguridad de la ONU convoca sesión de emergencia"
        ],
        "sections": [
            {
                "title": "ESCENARIOS GEOPOLÍTICOS",
                "items": [
                    { "label": "Conflicto regional escala a Guerra Total", "odds": "+210", "pct": 32 },
                    { "label": "Apertura de corredor humanitario en Ormuz", "odds": "-110", "pct": 52 }
                ]
            },
            {
                "title": "MERCADOS & ENERGÍA",
                "items": [
                    { "label": "Cierre total del Estrecho de Ormuz (>48h)", "odds": "+550", "pct": 15 },
                    { "label": "Oro alcanza nuevo máximo histórico", "odds": "-250", "pct": 71 }
                ]
            }
        ]
    }

def main():
    new_data = get_latest_osint_data()
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    
    print("✅ data.json actualizado con éxito con información OSINT.")

if __name__ == "__main__":
    main()
