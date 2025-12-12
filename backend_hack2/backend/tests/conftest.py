import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import mongomock
from main import app
from database import db


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def mock_db():
    """Mock MongoDB database."""
    # Use mongomock for testing
    mock_client = mongomock.MongoClient()
    mock_database = mock_client.test_db

    # Replace the global db
    original_db = db
    globals()['db'] = mock_database

    yield mock_database

    # Restore original db
    globals()['db'] = original_db


@pytest.fixture
def mock_httpx():
    """Mock httpx for external API calls."""
    with pytest.mock.patch('httpx.Client') as mock_client:
        yield mock_client.return_value


@pytest.fixture
def mock_groq():
    """Mock Groq LLM."""
    with pytest.mock.patch('agents.ChatGroq') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Test video prompt")
        mock_llm.return_value = mock_instance
        yield mock_llm


@pytest.fixture
def mock_genai():
    """Mock Google GenAI."""
    with pytest.mock.patch('agents.genai') as mock_genai:
        mock_client = MagicMock()
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result = MagicMock()
        mock_operation.result.generated_videos = [MagicMock(video=MagicMock(blob=b'test_video_bytes'))]
        mock_client.models.generate_videos.return_value = mock_operation
        mock_genai.Client.return_value = mock_client
        yield mock_genai
