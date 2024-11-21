from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ActionLog(Base):
    """
    Model for storing logs of user actions in the system.
    """
    __tablename__ = "action_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
