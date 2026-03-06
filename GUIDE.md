# Bookmarks API - Python Backend Guide for Node.js Developers

A beginner-friendly guide to understanding this FastAPI project. If you know Node.js/Express, you'll pick this up fast!

---

## 📁 Project Structure

```
mo_api/
├── main.py              # Entry point (like server.js in Express)
├── database.py          # DB connection setup
├── models.py            # ORM models (like Sequelize/TypeORM models)
├── schemas.py           # Request/response validation (like Zod schemas)
├── requirements.txt     # Dependencies (like package.json)
├── Dockerfile           # Container config
├── docker-compose.yml   # Multi-container orchestration
├── alembic/             # Database migrations
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
└── routers/             # Route handlers
    ├── collections.py
    └── bookmarks.py
```

---

## 🔄 How It Compares to Node.js

| Concept | Node.js / Express | Python / FastAPI |
|---------|------------------|------------------|
| **Framework** | Express | FastAPI |
| **ORM** | Sequelize, TypeORM | SQLAlchemy |
| **Validation** | Zod, Joi | Pydantic |
| **Async** | async/await | async/await (same!) |
| **Server startup** | `npm start` | `uvicorn main:app` |
| **Migrations** | TypeORM CLI, Knex | Alembic |

---

## 1️⃣ Understanding the Database Connection (`database.py`)

This is like your `db.js` or database config in Node.js.

```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/bookmarks"
```

Breaking it down:
- `postgresql` = Database type
- `+asyncpg` = Driver for async operations (like using `async/await` in Node)
- `user:password` = Credentials
- `localhost:5432` = Host and port
- `bookmarks` = Database name

### Creating an Engine & Session Maker

```python
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)
```

Think of this like:
- **engine** = Your database connection pool
- **async_session_maker** = A factory that creates DB sessions (like opening a transaction)

### The `get_db()` Function

```python
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

This is a **dependency injector** (FastAPI feature). Every route that needs a DB connection gets `get_db()` injected automatically. Think of it like Express middleware that passes `req.db` to your handlers.

---

## 2️⃣ ORM Models (`models.py`)

SQLAlchemy models define your database tables and relationships. Compare to Sequelize:

### Collection Model
```python
class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    bookmarks: Mapped[list["Bookmark"]] = relationship(...)
```

**Python syntax notes:**
- `Mapped[int]` = Type annotation (like TypeScript)
- `mapped_column(Integer, primary_key=True)` = Column definition
- `|` = Union type (like TypeScript's `|`). `str | None` means optional
- `relationship()` = Foreign key relationship to another model

### Bookmark Model
```python
class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(2048))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    collection_id: Mapped[int] = mapped_column(Integer, ForeignKey("collections.id"))
    collection: Mapped["Collection"] = relationship("Collection", back_populates="bookmarks")
```

**Key relationship:**
- `collection_id` = Foreign key (references `collections.id`)
- `collection` = Relationship object (lets you access the full Collection object)
- `back_populates="bookmarks"` = Two-way relationship (Collection can access its Bookmarks)

---

## 3️⃣ Validation Schemas (`schemas.py`)

These are like Zod/Joi in Node.js. They validate incoming requests and define response formats.

```python
class CollectionCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
```

Breaking it down:
- `BaseModel` = Pydantic's validation class
- `Field(..., max_length=255)` = Required field with validation
- `Optional[str]` = Nullable/optional field
- `...` = Required (like in TypeScript)

**Response Schema:**
```python
class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
```

The `from_attributes=True` tells Pydantic to read from SQLAlchemy model attributes. Without this, it won't work!

---

## 4️⃣ Route Handlers (Routers)

FastAPI routers are like Express route files.

### `routers/collections.py` Example

```python
@router.post("", response_model=CollectionResponse, status_code=201)
async def create_collection(
    data: CollectionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    collection = Collection(**data.model_dump())
    db.add(collection)
    await db.commit()
    await db.refresh(collection)
    return collection
```

**Breaking it down:**

| Part | Explanation |
|------|-------------|
| `@router.post("")` | Route: `POST /collections` (prefix added in main.py) |
| `response_model=CollectionResponse` | Return type validation (like response schema) |
| `status_code=201` | HTTP status (Created) |
| `data: CollectionCreate` | Request body validation using Pydantic |
| `db: Annotated[AsyncSession, Depends(get_db)]` | Dependency injection: inject DB session |
| `Collection(**data.model_dump())` | Create a model instance from request data |
| `db.add(collection)` | Stage for insertion (like `.save()` in Sequelize) |
| `await db.commit()` | Execute the transaction (like `.save()` completes) |
| `await db.refresh(collection)` | Reload from DB to get generated ID |
| `return collection` | FastAPI auto-converts to JSON using response_model |

### Querying (`list_collections`)

```python
@router.get("", response_model=list[CollectionResponse])
async def list_collections(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    result = await db.execute(
        select(Collection)
        .offset(skip)
        .limit(limit)
        .order_by(Collection.created_at.desc())
    )
    return result.scalars().all()
```

SQLAlchemy query builder (like TypeORM):
- `select(Collection)` = SELECT * FROM collections
- `.offset(skip)` = OFFSET clause (pagination)
- `.limit(limit)` = LIMIT clause
- `.order_by(Collection.created_at.desc())` = ORDER BY created_at DESC
- `result.scalars().all()` = Execute and return all rows

**In TypeORM/Sequelize:**
```typescript
// TypeORM equivalent:
const collections = await db.find(Collection, {
  skip: skip,
  take: limit,
  order: { created_at: 'DESC' }
});
```

### Update Example

```python
@router.patch("/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Collection).where(Collection.id == collection_id)
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="...")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(collection, field, value)

    await db.commit()
    await db.refresh(collection)
    return collection
```

Key points:
- `scalar_one_or_none()` = Get single result or None
- `exclude_unset=True` = Only include fields that were sent (partial updates)
- `setattr(collection, field, value)` = Dynamically set attributes
- Objects are modified in-place, then committed

---

## 5️⃣ Main App (`main.py`)

```python
from fastapi import FastAPI

app = FastAPI(
    title="Bookmarks API",
    description="A simple link-saving service with collections",
    version="1.0.0",
    lifespan=lifespan,
)
```

This creates the FastAPI app. Like `const app = express()` in Node.js.

### Exception Handlers

FastAPI lets you handle errors globally:

```python
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "detail": "..."},
    )
```

This is like Express error middleware.

### Router Registration

```python
app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(bookmarks.router, tags=["bookmarks"])
```

Like `app.use('/collections', collectionsRouter)` in Express.

### Lifespan Context Manager

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()
```

Cleanup code that runs when the app shuts down. Like `app.close()` in Node.js.

---

## 6️⃣ Docker & Docker Compose

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uvicorn[standard] fastapi sqlalchemy...

COPY . .

EXPOSE 8000

CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

**Breaking it down:**

| Line | What It Does |
|------|-------------|
| `FROM python:3.12-slim` | Base image: Python 3.12 (slim = smaller) |
| `WORKDIR /app` | Set working directory in container |
| `RUN pip install...` | Install dependencies (like npm install in Node) |
| `COPY . .` | Copy your code into the container |
| `EXPOSE 8000` | Tell Docker we listen on port 8000 |
| `CMD alembic upgrade head && uvicorn...` | Run migrations, then start the server |

### Docker Compose (`docker-compose.yml`)

Docker Compose runs multiple containers together (app + database).

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/bookmarks
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
```

**Breaking it down:**

| Key | Meaning |
|-----|---------|
| `build` | Build the Docker image from Dockerfile |
| `ports` | Map container port 8000 to your machine's port 8000 |
| `environment` | Set env vars inside the container |
| `depends_on: condition: service_healthy` | Wait for DB to be ready before starting app |
| `restart: unless-stopped` | Auto-restart on crash |

```yaml
  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=bookmarks
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d bookmarks"]
      interval: 5s
      timeout: 5s
      retries: 5
```

| Key | Meaning |
|-----|---------|
| `image: postgres:16` | Use official Postgres image |
| `environment` | Set Postgres user/password/database |
| `volumes: postgres_data:/var/lib/postgresql/data` | Persist data between container restarts |
| `healthcheck` | Check if Postgres is ready (the app waits for this) |

### Common Docker Compose Commands

```bash
# Start all containers (builds if needed)
docker compose up

# Start in background
docker compose up -d

# Rebuild images (use after changing Dockerfile)
docker compose up --build

# View logs
docker compose logs -f

# Stop containers
docker compose down

# Stop and remove volumes (deletes data!)
docker compose down -v

# Run a command in a container
docker compose exec app bash

# View running containers
docker compose ps
```

---

## 7️⃣ Database Migrations (Alembic)

Alembic is like Sequelize or Knex migrations in Node.js.

### Initial Migration (`alembic/versions/001_initial.py`)

```python
def upgrade() -> None:
    op.create_table(
        'collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        # ... other columns
        sa.PrimaryKeyConstraint('id')
    )
```

This defines:
- Table name
- Columns and types
- Constraints

### Running Migrations

In Docker, this runs automatically:
```dockerfile
CMD alembic upgrade head && uvicorn main:app ...
```

`alembic upgrade head` runs all pending migrations.

Locally, you'd run:
```bash
alembic upgrade head  # Run migrations
alembic downgrade -1  # Rollback one migration
```

---

## 8️⃣ Data Flow Example: Creating a Collection

Here's the complete flow:

### Request
```bash
POST /collections
Content-Type: application/json

{
  "name": "Web Development",
  "description": "Useful web dev resources"
}
```

### What Happens

1. **FastAPI validates** the request body using `CollectionCreate` schema
   ```python
   data: CollectionCreate  # Pydantic validates here
   ```

2. **Dependency injection** provides a DB session
   ```python
   db: Annotated[AsyncSession, Depends(get_db)]  # get_db() is called
   ```

3. **Create a model instance**
   ```python
   collection = Collection(**data.model_dump())
   # collection = Collection(name="Web Development", description="...")
   ```

4. **Stage and execute**
   ```python
   db.add(collection)           # Add to session
   await db.commit()            # Execute INSERT
   await db.refresh(collection) # Reload to get auto-generated ID
   ```

5. **FastAPI serializes the response** using `CollectionResponse` schema
   ```python
   return collection  # Auto-converts to JSON
   ```

6. **Response**
   ```json
   {
     "id": 1,
     "name": "Web Development",
     "description": "Useful web dev resources",
     "created_at": "2026-03-06T21:30:00"
   }
   ```

---

## 📝 Key Differences from Node.js

| Feature | Node.js | Python |
|---------|---------|--------|
| Type hints | Optional (TypeScript) | Built-in (type annotations) |
| Decorators | N/A | `@app.get()`, `@router.post()` |
| Async by default | Mostly async/await | async/await everywhere |
| ORM style | Class-based (Sequelize) | Class-based (SQLAlchemy) |
| Validation | Library (Zod, Joi) | Built-in (Pydantic) |
| Server | `npm start` | `uvicorn main:app` |
| Port | Usually 3000 | Usually 8000 |
| Container | `Dockerfile` | `Dockerfile` (same concept) |

---

## 🚀 Running the Project

### With Docker Compose (Recommended)

```bash
# Start everything
docker compose up --build

# Check logs
docker compose logs -f app

# Stop
docker compose down
```

Visit: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

### Locally (for development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

---

## 🔍 API Endpoints

### Collections
- `POST /collections` - Create
- `GET /collections` - List (paginated)
- `GET /collections/{id}` - Get one
- `PATCH /collections/{id}` - Update
- `DELETE /collections/{id}` - Delete

### Bookmarks
- `POST /collections/{collection_id}/bookmarks` - Create
- `GET /collections/{collection_id}/bookmarks` - List by collection
- `GET /bookmarks/{id}` - Get one
- `PATCH /bookmarks/{id}` - Update
- `DELETE /bookmarks/{id}` - Delete

Test with Swagger UI at `http://localhost:8000/docs`

---

## 💡 Pro Tips

1. **Type hints are your friend** - Python doesn't force them, but they help catch bugs
2. **Use `Optional[T]` for nullable fields** - Clearer than SQLAlchemy's `nullable=True`
3. **Always use `from_attributes=True`** in Pydantic schemas - Needed for ORM objects
4. **`depend_on` in docker-compose** - Wait for services to be healthy before starting
5. **Use `async/await` everywhere** - Avoid blocking operations in async functions
6. **`.model_dump(exclude_unset=True)`** - Perfect for partial updates (only send changed fields)

---

**That's it!** You now understand the whole project. Happy coding! 🚀
