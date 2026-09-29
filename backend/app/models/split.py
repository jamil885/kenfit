from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="USER",
    )

    owner = relationship("User")

    days = relationship(
        "SplitDay",
        back_populates="split",
        cascade="all, delete-orphan",
        order_by="SplitDay.order",
    )