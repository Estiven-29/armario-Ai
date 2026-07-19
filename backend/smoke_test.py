"""Prueba de humo de la API (requiere el servidor en localhost:8000)."""
import io

import requests
from PIL import Image

BASE = "http://127.0.0.1:8000"


def png(color):
    buf = io.BytesIO()
    Image.new("RGB", (80, 80), color).save(buf, format="PNG")
    return buf.getvalue()


def main():
    print("health:", requests.get(f"{BASE}/api/health").json())

    for name, color in [("azul", (30, 80, 200)), ("blanco", (245, 245, 245)), ("negro", (20, 20, 20))]:
        r = requests.post(f"{BASE}/api/items", files={"file": (f"{name}.png", png(color), "image/png")})
        r.raise_for_status()
        item = r.json()
        print(f"item {name}: id={item['id']} color={item['color_principal']} url={item['image_url']}")

    items = requests.get(f"{BASE}/api/items").json()
    print("total items:", len(items))

    # Editar categoría manualmente (human-in-the-loop)
    first = items[0]
    r = requests.patch(f"{BASE}/api/items/{first['id']}", json={"categoria": "superior", "tipo": "camiseta"})
    print("patched:", r.json()["categoria"], r.json()["tipo"])

    # Sugerir outfits (modo fallback sin key)
    r = requests.post(f"{BASE}/api/outfits/suggest", json={"ocasion": "casual", "clima": "templado"})
    print("suggest:", r.json())


if __name__ == "__main__":
    main()
