from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


async def make_item(db_session: AsyncSession, **overrides) -> Item:
    defaults = dict(title="Some Title", type="BOOK", genre="FICTION", author="Some Author", available=True)
    defaults.update(overrides)
    item = Item(**defaults)
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
