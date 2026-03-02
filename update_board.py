import os
import json
import sys
from datetime import datetime
from groq import Groq

# Configuración
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)

def update_data():
    today = datetime.now().strftime("%d de %B de %Y — %H:%M UTC")
    
    prompt = f"""
    Fecha actual: {today}
    Eres un analista senior de inteligencia. Genera un JSON para un tablero de cuotas geopolíticas (formato americano).
    
    REQUISITOS ESTRICTOS:
    1. Devuelve SOLO el objeto JSON.
    2. Debe tener 14 secciones (Macro, Irán, México, Cuba, Ucrania, Taiwán, Afganistán, Pakistán, China, Rusia, Corea del Norte, Interior EE.UU., Economía, Longshots).
    3. Cada sección debe tener un 'label', un 'flag' (emoji) y una lista de 'rows'.
    4. Cada 'row' debe tener: 'event', 'odds' (ej: -150, +200, o 'LIQUIDADO'), 'moved' ('up', 'down', 'none') y 'params' (una breve explicación).
    5. Incluye una lista 'ticker' con 15 noticias cortas e impactantes.
    6. Incluye una sección 'sources' con 3 fuentes reales de noticias de hoy.
    7. Incluye un campo 'methodology' breve.
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Analista de Inteligencia. Solo respondes con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        raw_content = completion.choices[0].message.content
        data = json.loads(raw_content)

        # Inyectar metadatos necesarios para el nuevo HTML
        data["lastUpdated"] = today
        
        # Guardar
        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Éxito: data.json actualizado con {len(data.get('sections', []))} secciones.")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY no encontrada.")
        sys.exit(1)
    update_data()
