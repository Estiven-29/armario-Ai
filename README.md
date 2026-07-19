# 👕 Armario IA

App web para digitalizar tu armario y crear outfits con ayuda de IA. Subes fotos de tus
prendas, una IA visual (**Google Gemini 2.0 Flash**) las categoriza automáticamente
(tipo, color, patrón, material, estilo, temporada, formalidad) y luego te sugiere outfits
razonados según la ocasión, el clima y reglas básicas de moda.

## Arquitectura

```
Frontend (React + Vite + TS)  ──HTTP/JSON──►  Backend (FastAPI)  ──►  Gemini (visión + moda)
                                                     │
                                              SQLite + /uploads
```

- **backend/** — API FastAPI, base de datos SQLite, imágenes en `backend/uploads/`.
- **frontend/** — SPA React (usable desde el móvil por el navegador).
- La categorización usa un **esquema JSON estricto** con listas cerradas de valores
  (ver `backend/app/taxonomy.py`) para que las etiquetas sean fiables, y el usuario puede
  **corregir** cualquier prenda (human-in-the-loop).
- Sin API key la app funciona en **modo de prueba** (detección de color local +
  combinaciones básicas); con key da categorización real y outfits razonados.

## Requisitos

- Python 3.12+
- Node.js 20+
- (Opcional pero recomendado) API key gratuita de Gemini: https://aistudio.google.com/apikey

## Puesta en marcha

### 1. Backend

```bash
cd backend
python -m venv .venv           # o: uv venv .venv
.venv\Scripts\activate         # Windows  (source .venv/bin/activate en Linux/Mac)
pip install -r requirements.txt

copy .env.example .env         # cp en Linux/Mac
# edita .env y pon tu GEMINI_API_KEY

uvicorn app.main:app --reload --port 8000
```

API en http://127.0.0.1:8000 · docs en http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App en http://localhost:5173 (proxy de `/api` y `/uploads` al backend).

## Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/items` | Sube una imagen → IA la categoriza |
| GET | `/api/items` | Lista prendas (filtros: categoria, estilo, color, temporada) |
| PATCH | `/api/items/{id}` | Corrige la categorización |
| DELETE | `/api/items/{id}` | Elimina una prenda |
| POST | `/api/outfits/suggest` | Sugiere outfits (ocasión, clima, preferencias) |
| GET/POST | `/api/outfits` | Lista / guarda outfits |
| GET | `/api/taxonomy` | Listas de valores permitidos |
| GET | `/api/health` | Estado + si la IA está activa |

## Prueba de humo

Con el backend corriendo:

```bash
cd backend
.venv\Scripts\python smoke_test.py
```

## Roadmap

- Fase 1 (MVP): subir prenda + categorización IA + galería ✅
- Fase 2: generar y guardar outfits con explicación ✅
- Fase 3: clima automático por API, planificación por calendario
- Fase 4: PWA / app móvil, autenticación multiusuario
