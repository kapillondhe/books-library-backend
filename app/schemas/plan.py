from pydantic import BaseModel


class PlanRead(BaseModel):
    id: int
    name: str
    max_books: int
    max_magazines: int

    model_config = {"from_attributes": True}
