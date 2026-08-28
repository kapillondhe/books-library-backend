from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db
from app.models.borrowing import Borrowing
from app.models.user import User
from app.schemas import BorrowingRead, UserCreate, UserRead
from app.services import create_user, get_user, list_user_borrowings

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def create_user_route(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    return await create_user(db, payload)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_route(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    return await get_user(db, user_id)


@router.get("/{user_id}/borrowings", response_model=list[BorrowingRead])
async def list_user_borrowings_route(user_id: int, db: AsyncSession = Depends(get_db)) -> list[Borrowing]:
    return await list_user_borrowings(db, user_id)
