from pydantic import BaseModel


class CategoryDTO(BaseModel):
    id: int
    description: str
    name: str
