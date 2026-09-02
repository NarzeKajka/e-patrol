from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[int] = mapped_column(primary_key=True)

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    x1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y1: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    x2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    y2: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    analysis = relationship(
        "Analysis",
        back_populates="detections",
    )