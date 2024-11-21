from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ActionLog(Base):
    """
    Model for storing logs of user actions in the system.
    """

    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
