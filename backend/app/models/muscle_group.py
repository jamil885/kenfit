from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    exercises = relationship(
        "ExerciseMuscle",
        back_populates="muscle_group",
        cascade="all, delete-orphan",
    )
