import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from cryptography.fernet import Fernet
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.password import hash_password
from app.config.settings import Settings, get_settings
from app.db.base import Base
from app.dependencies.auth import get_session, get_settings_dep
from app.main import app
from app.models.user import User

# Test database URL — use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://seo_user:change_me_in_production@localhost:5432/seo_db_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        JWT_SECRET_KEY="test-secret-key-for-testing-only-32chars",
        TOKEN_ENCRYPTION_KEY=Fernet.generate_key().decode(),
        SHOPIFY_API_KEY="test_api_key",
        SHOPIFY_API_SECRET="test_api_secret",
        DATABASE_URL=TEST_DATABASE_URL,
        DEBUG=True,
        APP_ENV="development",
        OPENAI_API_KEY="test_openai_key",
        SYNC_ENABLED=False,
        AI_REQUIRE_APPROVAL_FOR_WRITES=False,
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine(test_settings: Settings):
    engine = create_async_engine(str(test_settings.database_url), echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings_dep] = lambda: test_settings
    get_settings.cache_clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=hash_password("TestPass1"),
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user
