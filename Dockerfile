FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uvicorn[standard] fastapi sqlalchemy[asyncio] asyncpg pydantic pydantic-settings alembic python-dotenv

COPY . .

EXPOSE 8000

CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
