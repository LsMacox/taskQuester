from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    due_at: Optional[date] = None
    completed_at: Optional[date] = None
    is_completed: bool
    is_hidden: bool
