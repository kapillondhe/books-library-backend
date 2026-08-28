from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core import get_db
from app.models.plan import SubscriptionPlan
from app.models.user import User
from main import app


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False})
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def silver_plan(db_session: AsyncSession) -> SubscriptionPlan:
    plan = SubscriptionPlan(name="Silver", max_books=1, max_magazines=1)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def gold_plan(db_session: AsyncSession) -> SubscriptionPlan:
    plan = SubscriptionPlan(name="Gold", max_books=3, max_magazines=2)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest_asyncio.fixture
async def adult_user(db_session: AsyncSession, silver_plan: SubscriptionPlan) -> User:
    user = User(email="adult@example.com", name="Adult User", age=25, subscription_id=silver_plan.id)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def minor_user(db_session: AsyncSession, silver_plan: SubscriptionPlan) -> User:
    user = User(email="minor@example.com", name="Minor User", age=17, subscription_id=silver_plan.id)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
