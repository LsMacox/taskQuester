from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, Union


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    due_at: Union[Optional[datetime], Optional[date]] = None
    completed_at: Union[Optional[datetime], Optional[date]] = None
    is_completed: bool
    is_hidden: bool
