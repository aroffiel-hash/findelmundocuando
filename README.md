# ¿Fin del Mundo Cuándo?
### Tablero de Probabilidades Geopolítico

Tablero de inteligencia OSINT en tiempo real que muestra probabilidades implícitas de los principales escenarios de riesgo geopolítico global. Interfaz estilo terminal financiero, actualización automática cada 12 horas, operación completamente gratuita.

**[→ Ver tablero en vivo](https://findelmundocuando.netlify.app)**

---

## Qué hace

Cada 12 horas, un bot de GitHub Actions:

1. Consulta 4 fuentes RSS internacionales (Al Jazeera, Reuters, BBC World, AP) y filtra solo titulares geopolíticos
2. Envía esos titulares a Groq / LLaMA 3.3-70B con un prompt analítico de nivel OSINT
3. Groq genera un análisis completo: cuotas en formato americano, análisis causal por escenario, y base rate histórica
4. El resultado se guarda como `data.json` y se despliega automáticamente vía Netlify

El tablero no replica mercados de predicción — es síntesis analítica original. El valor está en los escenarios de cascada, riesgos nucleares, y efectos geopolíticos en México que los mercados no cubren bien.

---

## Secciones del tablero

| # | Sección | Enfoque |
|---|---------|---------|
| ☢️ | Irán y Oriente Medio | IRGC, Hormuz, coalición EE.UU.-Israel, Gulf states |
| 🇷🇺 | Rusia / Ucrania / OTAN | Ofensivas, doctrina nuclear, membresía OTAN |
| 🇨🇳 | China / Taiwán / Pacífico | Ventana de invasión, semiconductores, Mar del Sur |
| 🇰🇵 | Corea del Norte | Pruebas nucleares, ICBM, cooperación con Rusia |
| 🇵🇰 | Pakistán / Afganistán | Arsenal nuclear, inestabilidad, talibán |
| 🇺🇸 | EE.UU. — Interior | Poderes de guerra, midterms, reclutamiento |
| 🇲🇽 | México y Latinoamérica | T-MEC, remesas, peso, carteles, Sheinbaum |
| 💰 | Economía y Energía Global | Petróleo, recesión, Fed, Eurozona |
| ☠️ | Escenarios Macro y Longshots | Nuclear, WW3, IA militar, riesgos existenciales |

---

## Stack técnico
```
GitHub Actions  →  update_board.py  →  data.json  →  Netlify
     ↓                    ↓
  cada 12h          Groq / LLaMA 3.3-70B
                    + 4 fuentes RSS
```

| Componente | Tecnología | Costo |
|------------|-----------|-------|
| Frontend | HTML + React 18 (CDN) + Babel | Gratis |
| Hosting | Netlify (plan free) | Gratis |
| Automatización | GitHub Actions | Gratis |
| Modelo de IA | Groq API / LLaMA 3.3-70B | Gratis (free tier) |
| Fuentes | Al Jazeera · Reuters · BBC · AP — RSS públicos | Gratis |

**Costo total de operación: $0/mes**

---

## Archivos
```
/
├── index.html          # Frontend completo (React, single file)
├── data.json           # Datos actuales del tablero (auto-generado)
├── update_board.py     # Script principal — Groq + RSS → data.json
├── fetch_data.py       # Fallback sin API key — Polymarket (solo geo)
├── run_local.py        # Servidor local para desarrollo
└── .github/
    └── workflows/
        └── update_news.yml  # Workflow de actualización automática
```

---

## Configuración

### 1. Fork y configurar secreto de Groq

1. Obtén una API key gratuita en [console.groq.com](https://console.groq.com)
2. En tu repo de GitHub: **Settings → Secrets and variables → Actions → New repository secret**
3. Nombre: `GROQ_API_KEY` · Valor: tu clave

### 2. Habilitar GitHub Actions

En tu repo: **Actions → habilitar workflows**

El workflow corre automáticamente cada 12 horas. También puedes ejecutarlo manualmente desde la pestaña Actions → "Actualizar Noticias OSINT" → Run workflow.

### 3. Desplegar en Netlify

1. Conecta tu repo en [netlify.com](https://netlify.com)
2. Build command: *(vacío — es HTML estático)*
3. Publish directory: `/` (raíz del repo)
4. Deploy

Netlify detecta el push de `data.json` que hace GitHub Actions y redespliega automáticamente.

### 4. Correr localmente
```bash
pip install requests
python run_local.py
# Abre http://localhost:8000
```

Para generar datos localmente:
```bash
GROQ_API_KEY=tu-llave python update_board.py
```

---

## Cómo funciona el análisis

El prompt enviado a Groq instruye al modelo a actuar como analista OSINT de nivel senior con reglas explícitas:

- **No duplicar Polymarket** — cubre escenarios de cascada y segunda derivada que los mercados no modelan bien
- **Params analíticos** — cada escenario incluye: mecanismo causal, condición necesaria, base rate histórica, y factor crítico que cambiaría la cuota
- **México obligatorio** — aranceles Trump, remesas, T-MEC, carteles, postura de Sheinbaum
- **Filtro de contenido** — post-procesado elimina cualquier row de entretenimiento o deportes que se cuele

Las cuotas están en formato americano (`-150` = favorito, `+300` = no favorito) y se convierten a probabilidad implícita para la barra de progreso.

---

## Panel lateral

El tablero incluye tres elementos fijos en el panel derecho:

- **Cuotas destacadas** — top 4 favoritos + top 3 longshots geopolíticos del ciclo actual
- **Reloj del Juicio Final** — actualizado al 27 de enero de 2026: **85 segundos para medianoche** (Bulletin of Atomic Scientists). Récord histórico desde 1947.
- **Carrusel de visualizaciones** — línea de tiempo 2023–2026, distribución de arsenales nucleares, red de conflictos activos

---

## Notas

- Las cuotas son síntesis analítica especulativa, **no son asesoramiento financiero ni de inteligencia**
- El Reloj del Juicio Final es dato hardcodeado — actualizar manualmente si el Bulletin lo mueve
- Si Groq no está disponible, `fetch_data.py` corre como fallback con datos de Polymarket filtrados estrictamente a contenido geopolítico

---

*Creado por **Adrián Roffiel** · Febrero 2026 · México*
