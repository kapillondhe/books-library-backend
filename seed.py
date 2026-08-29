"""Populate the database with sample subscription plans and catalog items."""

import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.item import Item
from app.models.plan import SubscriptionPlan

PLANS = [
    {"name": "Silver", "max_books": 2, "max_magazines": 0},
    {"name": "Gold", "max_books": 3, "max_magazines": 1},
    {"name": "Platinum", "max_books": 4, "max_magazines": 2},
]

ITEMS = [
    {
        "title": "Ramayana",
        "type": "BOOK",
        "genre": "MYTHOLOGY",
        "author": "Valmiki",
        "description": "The epic tale of Prince Rama's exile, the abduction of Sita, and the war against Ravana.",
    },
    {
        "title": "Mahabharata",
        "type": "BOOK",
        "genre": "MYTHOLOGY",
        "author": "Vyasa",
        "description": "The epic chronicle of the Kurukshetra war and the rivalry between the Pandavas and Kauravas.",
    },
    {
        "title": "Crime and Punishment",
        "type": "BOOK",
        "genre": "CRIME",
        "author": "Fyodor Dostoevsky",
        "description": "A poverty-stricken ex-student in Saint Petersburg wrestles with guilt after committing murder.",
    },
    {
        "title": "White Nights",
        "type": "BOOK",
        "genre": "FICTION",
        "author": "Fyodor Dostoevsky",
        "description": "A lonely dreamer falls for a young woman over four nights in Saint Petersburg.",
    },
    {
        "title": "The Hobbit",
        "type": "BOOK",
        "genre": "FANTASY",
        "author": "J.R.R. Tolkien",
        "description": "A reluctant hobbit sets out on an epic quest to reclaim a dwarf kingdom.",
    },
    {
        "title": "Harry Potter and the Sorcerer's Stone",
        "type": "BOOK",
        "genre": "FANTASY",
        "author": "J.K. Rowling",
        "description": "A young wizard discovers his magical heritage on the eve of his eleventh birthday.",
    },
    {
        "title": "The Pragmatic Programmer",
        "type": "BOOK",
        "genre": "PROGRAMMING",
        "author": "David Thomas, Andrew Hunt",
        "description": "A guide to practical, pragmatic approaches to software craftsmanship.",
    },
    {
        "title": "Extreme Programming Explained",
        "type": "BOOK",
        "genre": "PROGRAMMING",
        "author": "Kent Beck",
        "description": "An introduction to the values and practices of the Extreme Programming methodology.",
    },
    {
        "title": "Sapiens",
        "type": "BOOK",
        "genre": "NON-FICTION",
        "author": "Yuval Noah Harari",
        "description": "A brief history of humankind, from the Stone Age to the modern era.",
    },
    {
        "title": "The Almanack of Naval Ravikant",
        "type": "BOOK",
        "genre": "NON-FICTION",
        "author": "Eric Jorgenson",
        "description": "A curated collection of Naval Ravikant's wisdom on wealth and happiness.",
    },
    {
        "title": "National Geographic",
        "type": "MAGAZINE",
        "genre": "SCIENCE",
        "author": "National Geographic Society",
        "description": "Monthly magazine covering geography, science, and world culture.",
    },
    {
        "title": "TIME",
        "type": "MAGAZINE",
        "genre": "NEWS",
        "author": "Time USA, LLC",
        "description": "Weekly news magazine covering current events and global affairs.",
    },
    {
        "title": "The Economist",
        "type": "MAGAZINE",
        "genre": "NEWS",
        "author": "The Economist Group",
        "description": "Weekly publication covering international news, economics, and business.",
    },
]


async def seed_plans(session) -> None:
    result = await session.execute(select(SubscriptionPlan))
    existing_names = {plan.name for plan in result.scalars().all()}

    for plan_data in PLANS:
        if plan_data["name"] not in existing_names:
            session.add(SubscriptionPlan(**plan_data))

    await session.commit()


async def seed_items(session) -> None:
    result = await session.execute(select(Item))
    if result.scalars().first() is not None:
        print("Items already seeded, skipping.")
        return

    for item_data in ITEMS:
        session.add(Item(**item_data))

    await session.commit()


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed_plans(session)
        await seed_items(session)

    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
