from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, Union


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    start_datetime: Union[Optional[datetime], Optional[date]] = None
    end_datetime: Union[Optional[datetime], Optional[date]] = None
    is_completed: bool
