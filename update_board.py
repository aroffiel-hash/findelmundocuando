import os
import json
import requests

def get_llama3_analysis():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: No se encontró GROQ_API_KEY.")
        return None

    # Instrucciones ultra-detalladas para que use TUS secciones originales
    prompt = """
    Eres un analista senior de inteligencia OSINT. Estamos en marzo de 2026.
    Debes generar un informe de situación en formato JSON para un Geopolitical Odds Board.
    
    ESTRUCTURA DE DATOS REQUERIDA (JSON):
    Debes devolver un objeto con "ticker" (mínimo 8 noticias) y "sections" (las 4 secciones de abajo).
    
    SECCIONES Y EVENTOS A EVALUAR:
    1. 🌍 ESCENARIOS MACRO (Flag: 🌍)
       - Conflicto regional escala a Guerra Total
       - El conflicto se mantiene solo regional
       - Corredor humanitario en Ormuz activado
    
    2. 🛢️ ENERGÍA & MERCADOS (Flag: 🛢️)
       - Cierre total Estrecho de Ormuz (>48h)
       - Brent supera los $120/barril
       - Oro alcanza nuevo máximo histórico
    
    3. 🇲🇽 MÉXICO & LATAM (Flag: 🇲🇽)
       - Peso mexicano (MXN) cae 10% vs USD
       - Sheinbaum convoca a cumbre regional de paz
    
    4. 🇮🇱 ISRAEL / REGIONAL (Flag: 🇮🇱)
       - Cúpula de Hierro saturada / 12m
       - Operación terrestre en Líbano sur
    
    PARA CADA EVENTO DEBES GENERAR:
    - "event": El nombre del evento (exacto a los de arriba).
    - "odds": Un valor entre +500 y -500 (ej: "-150", "+210").
    - "params": Una explicación analítica breve (máx 140 caracteres) de por qué se mueve el indicador en MARZO 2026.
    - "moved": "up", "down" o "none" según la tendencia actual.

    IMPORTANTE: El tono debe ser profesional, urgente y basado en los eventos de marzo 2026 (ataques del CGRI, USS Abraham Lincoln, etc).
    Devuelve SOLO el JSON.
    """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7, # Para que las noticias varíen un poco cada vez
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    ai_content = get_llama3_analysis()
    if ai_content:
        data = json.loads(ai_content)
        # Aseguramos que los nombres de las llaves coincidan con el index.html
        # (Llama 3 a veces pone 'label' en lugar de 'title')
        for sec in data.get('sections', []):
            if 'title' in sec and 'label' not in sec:
                sec['label'] = sec['title']
            if 'items' in sec and 'rows' not in sec:
                sec['rows'] = sec['items']

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("✅ Board actualizado con todos los indicadores originales.")

if __name__ == "__main__":
    main()
