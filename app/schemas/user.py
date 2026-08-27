from pydantic import BaseModel, EmailStr

from app.schemas.plan import PlanRead


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    age: int
    subscription_id: int


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    age: int
    subscription_id: int
    subscription_plan: PlanRead

    model_config = {"from_attributes": True}
