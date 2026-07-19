import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import ai, models, schemas
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/items", tags=["items"])

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _to_out(item: models.Item) -> schemas.ItemOut:
    out = schemas.ItemOut.model_validate(item)
    out.image_url = f"/uploads/{Path(item.image_path).name}"
    return out


@router.post("", response_model=schemas.ItemOut)
async def create_item(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Formato no soportado (usa JPG, PNG o WEBP)")

    data = await file.read()
    if len(data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen supera los 10 MB")

    filename = f"{uuid.uuid4().hex}{_EXT[file.content_type]}"
    filepath = settings.uploads_dir / filename
    filepath.write_bytes(data)

    try:
        cats = ai.categorize_image(data, file.content_type)
    except Exception:  # la IA no debe bloquear el guardado
        color = ai.dominant_color(data)
        cats = {
            "nombre": "", "categoria": "", "tipo": "", "color_principal": color,
            "colores": [color], "patron": "liso", "material": "desconocido",
            "estilo": "casual", "temporada": "todo el año", "formalidad": 3,
            "ai_confianza": 0.0,
        }

    item = models.Item(image_path=str(filepath), **cats)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.get("", response_model=list[schemas.ItemOut])
def list_items(
    categoria: str | None = None,
    estilo: str | None = None,
    temporada: str | None = None,
    color: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Item)
    if categoria:
        q = q.filter(models.Item.categoria == categoria)
    if estilo:
        q = q.filter(models.Item.estilo == estilo)
    if temporada:
        q = q.filter(models.Item.temporada == temporada)
    if color:
        q = q.filter(models.Item.color_principal == color)
    items = q.order_by(models.Item.created_at.desc()).all()
    return [_to_out(i) for i in items]


@router.patch("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Prenda no encontrada")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return _to_out(item)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Prenda no encontrada")
    try:
        Path(item.image_path).unlink(missing_ok=True)
    except OSError:
        pass
    db.delete(item)
    db.commit()
