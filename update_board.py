import os
import json
import requests

def get_llama3_analysis():
    # Buscamos la llave de Groq en los secretos de GitHub
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: No se encontró GROQ_API_KEY en los secretos.")
        return None

    # Las instrucciones para la IA. Le pedimos que use la estructura original de tu Board.
    prompt = """
    Eres un analista de inteligencia OSINT y geopolítica. Estamos en marzo de 2026.
    Tu trabajo es evaluar la situación global (Irán, Medio Oriente, mercados, México) y actualizar un panel de "Odds" (probabilidades).
    
    Debes devolver ÚNICAMENTE un objeto JSON válido con la siguiente estructura exacta:
    {
      "ticker": [
         "⚡ [Noticia corta impactante 1]", 
         "🔴 [Noticia corta 2]",
         "🛢️ [Noticia sobre petróleo/mercados]"
      ],
      "sections": [
        {
          "flag": "🌍",
          "label": "ESCENARIOS MACRO",
          "rows": [
            { "event": "Conflicto regional escala a Guerra Total", "odds": "+210", "params": "Razón en 1 o 2 oraciones.", "moved": "down" },
            { "event": "El conflicto se mantiene solo regional", "odds": "-380", "params": "Justificación analítica.", "moved": "up" }
          ]
        },
        {
          "flag": "🇲🇽",
          "label": "MÉXICO",
          "rows": [
            { "event": "Peso mexicano cae 10%+ frente al dólar en 30 días", "odds": "+170", "params": "Justificación económica.", "moved": "none" }
          ]
        }
      ]
    }
    
    Reglas:
    1. Genera al menos 5 items para el "ticker".
    2. Mantén los valores "moved" limitados a: "up", "down", o "none".
    3. Inventa un análisis realista para marzo 2026 basado en el contexto de tensión entre EE.UU., Israel e Irán.
    4. NO devuelvas texto fuera del JSON.
    """

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192", # El modelo Open Source más inteligente
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        print("Consultando a Llama 3 vía Groq...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Fallo en la conexión: {e}")
        return None

def main():
    ai_content = get_llama3_analysis()
    
    if ai_content:
        # Validamos que el JSON sea correcto antes de escribirlo
        try:
            data = json.loads(ai_content)
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("✅ Board OSINT actualizado con éxito usando Llama 3.")
        except json.JSONDecodeError:
            print("Error: Llama 3 no devolvió un JSON válido.")
    else:
        print("No se pudo obtener análisis de la IA.")

if __name__ == "__main__":
    main()
