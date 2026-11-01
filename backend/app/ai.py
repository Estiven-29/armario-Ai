"""Motor de IA: categorización de prendas y sugerencia de outfits con Gemini.

Si no hay API key configurada, se usan heurísticas locales (modo de prueba) para
que la app siga siendo funcional.
"""

from __future__ import annotations

import io
import json
from typing import Any

from PIL import Image

from .config import settings
from . import taxonomy

# --- Colores nombrados (RGB de referencia) para el modo sin IA -----------------
_COLOR_RGB: dict[str, tuple[int, int, int]] = {
    "negro": (20, 20, 20),
    "blanco": (245, 245, 245),
    "gris": (128, 128, 128),
    "azul": (30, 80, 200),
    "azul marino": (20, 30, 80),
    "celeste": (140, 200, 235),
    "rojo": (200, 40, 40),
    "rosa": (235, 150, 190),
    "verde": (40, 160, 80),
    "amarillo": (235, 220, 60),
    "naranja": (235, 140, 40),
    "morado": (130, 60, 170),
    "marron": (110, 70, 40),
    "beige": (220, 200, 160),
    "camel": (190, 150, 100),
    "crema": (240, 235, 210),
}


def _closest_color(rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    best, best_d = "gris", float("inf")
    for name, (cr, cg, cb) in _COLOR_RGB.items():
        d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if d < best_d:
            best, best_d = name, d
    return best


def flatten_on_white(image_bytes: bytes) -> bytes:
    """Compone la imagen (p.ej. PNG sin fondo) sobre blanco y devuelve PNG.

    Los píxeles transparentes suelen tener RGB negro; así ni Gemini ni la detección
    de color los confunden con una prenda negra.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    out = Image.alpha_composite(bg, img).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()


def dominant_color(image_bytes: bytes) -> str:
    """Color más cercano de la prenda, ignorando píxeles transparentes."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA").resize((50, 50))
        pixels = [p[:3] for p in img.getdata() if p[3] > 128]
        if not pixels:
            return "gris"
        avg = tuple(sum(c) // len(pixels) for c in zip(*pixels))
        return _closest_color(avg)  # type: ignore[arg-type]
    except Exception:
        return "gris"


# --- Cliente Gemini ------------------------------------------------------------
def _client():
    from google import genai

    return genai.Client(api_key=settings.gemini_api_key)


def _categorize_schema():
    from google.genai import types

    def enum_prop(values: list[str]) -> types.Schema:
        return types.Schema(type=types.Type.STRING, enum=[str(v) for v in values])

    return types.Schema(
        type=types.Type.OBJECT,
        required=["categoria", "tipo", "color_principal", "estilo", "temporada", "formalidad"],
        properties={
            "nombre": types.Schema(type=types.Type.STRING),
            "categoria": enum_prop(taxonomy.CATEGORIAS),
            "tipo": enum_prop(taxonomy.TIPOS),
            "color_principal": enum_prop(taxonomy.COLORES),
            "colores": types.Schema(type=types.Type.ARRAY, items=enum_prop(taxonomy.COLORES)),
            "patron": enum_prop(taxonomy.PATRONES),
            "material": enum_prop(taxonomy.MATERIALES),
            "estilo": enum_prop(taxonomy.ESTILOS),
            "temporada": enum_prop(taxonomy.TEMPORADAS),
            "formalidad": types.Schema(type=types.Type.INTEGER),
            "confianza": types.Schema(type=types.Type.NUMBER),
        },
    )


_CATEGORIZE_PROMPT = (
    "Eres un estilista experto en moda. Analiza la prenda de la foto y clasifícala "
    "con precisión. Devuelve SOLO los valores permitidos por el esquema. "
    "'formalidad' va de 1 (muy informal) a 5 (muy formal). "
    "'confianza' es tu certeza de 0 a 1. Sé fiel a lo que ves: color real, tipo exacto "
    "de prenda, material aparente y temporada más adecuada. "
    "Genera un 'nombre' corto y descriptivo (p.ej. 'Camisa blanca lino')."
)


def categorize_image(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    color = dominant_color(image_bytes)
    if not settings.ai_enabled:
        return {
            "nombre": "",
            "categoria": "",
            "tipo": "",
            "color_principal": color,
            "colores": [color],
            "patron": "liso",
            "material": "desconocido",
            "estilo": "casual",
            "temporada": "todo el año",
            "formalidad": 3,
            "ai_confianza": 0.0,
        }

    from google.genai import types

    # Gemini recibe la prenda sobre fondo blanco (si venía recortada con alfa).
    try:
        image_bytes, mime_type = flatten_on_white(image_bytes), "image/png"
    except Exception:
        pass

    client = _client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            _CATEGORIZE_PROMPT,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_categorize_schema(),
            temperature=0.2,
        ),
    )
    data = json.loads(response.text)
    return {
        "nombre": data.get("nombre", ""),
        "categoria": data.get("categoria", ""),
        "tipo": data.get("tipo", ""),
        "color_principal": data.get("color_principal", color),
        "colores": data.get("colores") or [data.get("color_principal", color)],
        "patron": data.get("patron", "liso"),
        "material": data.get("material", "desconocido"),
        "estilo": data.get("estilo", "casual"),
        "temporada": data.get("temporada", "todo el año"),
        "formalidad": int(data.get("formalidad", 3)),
        "ai_confianza": float(data.get("confianza", 0.0)),
    }


# --- Sugerencia de outfits -----------------------------------------------------
def _item_line(it: Any) -> str:
    return (
        f"id={it.id} | {it.categoria}/{it.tipo} | color={it.color_principal} | "
        f"estilo={it.estilo} | formalidad={it.formalidad} | temporada={it.temporada}"
    )


_OUTFIT_PROMPT = (
    "Eres un estilista personal. A partir del inventario del armario, crea {n} outfits "
    "coherentes para la ocasión y el clima indicados. Reglas de moda: coherencia de "
    "formalidad, armonía de color (neutros + un acento), adecuación a la temporada/clima, "
    "y equilibrio superior/inferior o un vestido. Cada outfit debe incluir al menos una "
    "prenda superior + inferior (o un vestido) y, si aplica, calzado. Usa SOLO ids del "
    "inventario. Explica brevemente el porqué de cada combinación.\n\n"
    "Ocasión: {ocasion}\nClima: {clima}\nPreferencias: {preferencias}\n\n"
    "Inventario:\n{inventario}"
)


def _outfit_schema():
    from google.genai import types

    return types.Schema(
        type=types.Type.OBJECT,
        required=["sugerencias"],
        properties={
            "sugerencias": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    required=["nombre", "item_ids", "razon"],
                    properties={
                        "nombre": types.Schema(type=types.Type.STRING),
                        "item_ids": types.Schema(
                            type=types.Type.ARRAY, items=types.Schema(type=types.Type.INTEGER)
                        ),
                        "razon": types.Schema(type=types.Type.STRING),
                    },
                ),
            )
        },
    )


def _fallback_outfits(items: list[Any], ocasion: str, n: int) -> list[dict[str, Any]]:
    superiores = [i for i in items if i.categoria == "superior"]
    inferiores = [i for i in items if i.categoria == "inferior"]
    vestidos = [i for i in items if i.categoria == "vestido"]
    calzados = [i for i in items if i.categoria == "calzado"]

    sugerencias: list[dict[str, Any]] = []
    combos = min(n, max(len(superiores) * min(len(inferiores), 1), len(vestidos)))
    for idx in range(max(combos, 0)):
        ids: list[int] = []
        if idx < len(vestidos) and not superiores:
            ids.append(vestidos[idx].id)
        else:
            if superiores:
                ids.append(superiores[idx % len(superiores)].id)
            if inferiores:
                ids.append(inferiores[idx % len(inferiores)].id)
        if calzados:
            ids.append(calzados[idx % len(calzados)].id)
        if ids:
            sugerencias.append(
                {
                    "nombre": f"Outfit {idx + 1} ({ocasion})",
                    "item_ids": ids,
                    "razon": "Combinación básica generada sin IA (configura la API key de Gemini "
                    "para sugerencias razonadas según moda, color y clima).",
                }
            )
    return sugerencias


def suggest_outfits(
    items: list[Any], ocasion: str, clima: str, preferencias: str, n: int
) -> tuple[list[dict[str, Any]], bool]:
    if not items:
        return [], settings.ai_enabled
    if not settings.ai_enabled:
        return _fallback_outfits(items, ocasion, n), False

    from google.genai import types

    inventario = "\n".join(_item_line(it) for it in items)
    prompt = _OUTFIT_PROMPT.format(
        n=n, ocasion=ocasion, clima=clima or "no especificado",
        preferencias=preferencias or "ninguna", inventario=inventario,
    )
    client = _client()
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_outfit_schema(),
            temperature=0.7,
        ),
    )
    data = json.loads(response.text)
    valid_ids = {it.id for it in items}
    sugerencias = [
        s for s in data.get("sugerencias", [])
        if s.get("item_ids") and all(i in valid_ids for i in s["item_ids"])
    ]
    return sugerencias, True
