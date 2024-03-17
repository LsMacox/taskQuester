from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    start_datetime: date
    end_datetime: Optional[date] = None
    is_completed: bool
