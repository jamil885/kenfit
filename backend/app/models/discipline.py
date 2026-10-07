from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Discipline(Base):
    __tablename__ = "disciplines"
    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
