from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import ai, models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/outfits", tags=["outfits"])


@router.post("/suggest", response_model=schemas.OutfitSuggestResponse)
def suggest(payload: schemas.OutfitSuggestRequest, db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    if not items:
        raise HTTPException(status_code=400, detail="Añade prendas antes de generar outfits")
    sugerencias, ai_usada = ai.suggest_outfits(
        items, payload.ocasion, payload.clima, payload.preferencias, payload.n_sugerencias
    )
    return schemas.OutfitSuggestResponse(sugerencias=sugerencias, ai_usada=ai_usada)


@router.post("", response_model=schemas.OutfitOut)
def save_outfit(payload: schemas.OutfitSave, db: Session = Depends(get_db)):
    outfit = models.Outfit(**payload.model_dump())
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit


@router.get("", response_model=list[schemas.OutfitOut])
def list_outfits(db: Session = Depends(get_db)):
    return db.query(models.Outfit).order_by(models.Outfit.created_at.desc()).all()


@router.delete("/{outfit_id}", status_code=204)
def delete_outfit(outfit_id: int, db: Session = Depends(get_db)):
    outfit = db.get(models.Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit no encontrado")
    db.delete(outfit)
    db.commit()
