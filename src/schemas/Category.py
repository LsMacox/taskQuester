from pydantic import BaseModel


class Category(BaseModel):
    id: int
    description: str
    name: str

