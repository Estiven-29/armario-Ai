from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import taxonomy
from .config import settings
from .database import init_db
from .routers import items, outfits

app = FastAPI(title="Armario IA", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()


app.mount("/uploads", StaticFiles(directory=str(settings.uploads_dir)), name="uploads")

app.include_router(items.router)
app.include_router(outfits.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "ai_enabled": settings.ai_enabled}


@app.get("/api/taxonomy")
def get_taxonomy() -> dict:
    return {
        "categorias": taxonomy.CATEGORIAS,
        "tipos": taxonomy.TIPOS,
        "colores": taxonomy.COLORES,
        "patrones": taxonomy.PATRONES,
        "materiales": taxonomy.MATERIALES,
        "estilos": taxonomy.ESTILOS,
        "temporadas": taxonomy.TEMPORADAS,
        "formalidad": taxonomy.FORMALIDAD,
        "ocasiones": taxonomy.OCASIONES,
    }
