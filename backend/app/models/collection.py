"""Collection ORM model: user_collection."""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserCollection(Base):
    """Represents a user's owned card collection."""

    __tablename__ = "user_collection"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "card_id", name="uq_user_collection_user_id_card_id"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cards.id"), nullable=False
    )
    quantity_owned: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="collection")
    card: Mapped["Card"] = relationship("Card", back_populates="collection_entries")
