from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_path: Mapped[str] = mapped_column(String(500))
    nombre: Mapped[str] = mapped_column(String(200), default="")
    categoria: Mapped[str] = mapped_column(String(50), default="")
    tipo: Mapped[str] = mapped_column(String(50), default="")
    color_principal: Mapped[str] = mapped_column(String(50), default="")
    colores: Mapped[list] = mapped_column(JSON, default=list)
    patron: Mapped[str] = mapped_column(String(50), default="liso")
    material: Mapped[str] = mapped_column(String(50), default="desconocido")
    estilo: Mapped[str] = mapped_column(String(50), default="casual")
    temporada: Mapped[str] = mapped_column(String(50), default="todo el año")
    formalidad: Mapped[int] = mapped_column(Integer, default=3)
    notas: Mapped[str] = mapped_column(Text, default="")
    ai_confianza: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), default="")
    ocasion: Mapped[str] = mapped_column(String(50), default="casual")
    item_ids: Mapped[list] = mapped_column(JSON, default=list)
    razon: Mapped[str] = mapped_column(Text, default="")
    favorito: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
