from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    nombre: str = ""
    categoria: str = ""
    tipo: str = ""
    color_principal: str = ""
    colores: list[str] = Field(default_factory=list)
    patron: str = "liso"
    material: str = "desconocido"
    estilo: str = "casual"
    temporada: str = "todo el año"
    formalidad: int = 3
    notas: str = ""


class ItemUpdate(BaseModel):
    nombre: str | None = None
    categoria: str | None = None
    tipo: str | None = None
    color_principal: str | None = None
    colores: list[str] | None = None
    patron: str | None = None
    material: str | None = None
    estilo: str | None = None
    temporada: str | None = None
    formalidad: int | None = None
    notas: str | None = None


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_path: str
    image_url: str = ""
    ai_confianza: float = 0.0
    created_at: datetime


class OutfitSuggestRequest(BaseModel):
    ocasion: str = "casual"
    clima: str = ""  # p.ej. "frío 8°C", "calor 30°C", "lluvia"
    preferencias: str = ""
    n_sugerencias: int = 3


class OutfitSuggestion(BaseModel):
    nombre: str
    item_ids: list[int]
    razon: str


class OutfitSuggestResponse(BaseModel):
    sugerencias: list[OutfitSuggestion]
    ai_usada: bool


class OutfitSave(BaseModel):
    nombre: str = ""
    ocasion: str = "casual"
    item_ids: list[int]
    razon: str = ""
    favorito: bool = False


class OutfitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ocasion: str
    item_ids: list[int]
    razon: str
    favorito: bool
    created_at: datetime
