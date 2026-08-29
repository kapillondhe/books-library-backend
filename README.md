# Books Library API

An async FastAPI backend for an online books/magazines library: users subscribe to a plan, browse the catalog, and order/return items, with borrowing limits enforced per subscription tier.

## Tech Stack

- **FastAPI** (async) — HTTP API
- **SQLAlchemy 2.0** (async ORM) — data access
- **PostgreSQL** (via `asyncpg`) — primary database (SQLite/`aiosqlite` supported for local/tests)
- **Pydantic v2 / pydantic-settings** — schemas & config
- **pytest / pytest-asyncio / httpx** — testing

## Project Structure

```
app/
  api/v1/          # Route handlers (users, items, borrowings, plans)
  core/            # App config and database session setup
  models/          # SQLAlchemy ORM models + enums
  schemas/         # Pydantic request/response schemas
  services/        # Business logic (user & borrowing workflows)
tests/             # API and service tests
main.py            # FastAPI app entrypoint
seed.py            # Seeds subscription plans and sample items
```

## Domain Overview

- A **User** subscribes to one **SubscriptionPlan** (e.g. Silver/Gold/Platinum), which caps how many books and magazines they may have borrowed at once.
- An **Item** is either a `BOOK` or `MAGAZINE`, with a `Genre`, and is `available` when not currently borrowed.
- A **Borrowing** links a user to an item for the duration it's checked out (`borrowed_at` → `returned_at`).
- A **Transaction** records each `ORDER`/`RETURN` action a user makes, used to enforce a monthly activity limit.

### Business Rules

- A user can have at most 10 order/return transactions per calendar month.
- Users under 18 cannot borrow `CRIME` genre items.
- Active borrowings (not yet returned) cannot exceed the user's plan quota for books/magazines.

## API Endpoints

All routes are prefixed with `/api/v1`.

| Method | Path                          | Description                     |
| ------ | ----------------------------- | ------------------------------- |
| GET    | `/`                           | Health check                    |
| POST   | `/users`                      | Create a user                   |
| GET    | `/users/{user_id}`            | Get a user                      |
| GET    | `/users/{user_id}/borrowings` | List a user's borrowing history |
| GET    | `/items`                      | List all items                  |
| POST   | `/items`                      | Create an item                  |
| GET    | `/plans`                      | List subscription plans         |
| POST   | `/borrowings/order`           | Order (borrow) an item          |
| POST   | `/borrowings/return`          | Return one or more items        |

Interactive docs are available at `/docs` (Swagger UI)

## Setup

1. **Install dependencies**

   ```bash
   uv pip install --python .venv/bin/python -r requirements.txt
   ```

2. **Configure environment** — create a `.env` file:

   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_db
   ```

   Falls back to a sensible local default if unset. `postgresql://` and `postgres://` URLs are automatically rewritten to use the `asyncpg` driver.

3. **Run the app**

   ```bash
   fastapi dev main.py
   ```

   Tables are created automatically on startup

4. **Seed sample data** (subscription plans + items)

   ```bash
   python seed.py
   ```

## Testing

```bash
pytest
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    SUBSCRIPTION_PLANS ||--o{ USERS : "subscribes"
    USERS ||--o{ BORROWINGS : "borrows"
    USERS ||--o{ TRANSACTIONS : "performs"
    ITEMS ||--o{ BORROWINGS : "is borrowed via"

    SUBSCRIPTION_PLANS {
        int id PK
        string name UK
        int max_books
        int max_magazines
    }

    USERS {
        int id PK
        string email UK
        string name
        int age
        int subscription_id FK
    }

    ITEMS {
        int id PK
        string title
        enum type
        enum genre
        string author
        text description
        bool available
    }

    BORROWINGS {
        int id PK
        int user_id FK
        int item_id FK
        datetime borrowed_at
        datetime returned_at
    }

    TRANSACTIONS {
        int id PK
        int user_id FK
        enum type
        datetime created_at
    }
```
