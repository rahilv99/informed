import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from .streaming_server import app, PodcastRequest

client = TestClient(app)

@pytest.fixture
def mock_generate_script():
    with patch("logic.streaming_server.generate_script") as mock:
        mock.return_value = "**HOST 1**: This is a test script.\n**HOST 2**: This is another test script."
        yield mock

@pytest.fixture
def mock_generate_email_headers():
    with patch("logic.streaming_server.generate_email_headers") as mock:
        mock.return_value = (
            [{"title": "Test Title", "description": "Test Description"}],
            "Test Episode Title"
        )
        yield mock

def test_generate_podcast(mock_generate_script, mock_generate_email_headers, capsys):
    # Arrange
    payload = {
        "user_id": "test_user",
        "episode": "test_episode",
        "plan": "free"
    }

    # Act
    response = client.post("/api/podcasts/generate", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()
    print(data)  # Print the response data for debugging

    # Capture and display the output
    captured = capsys.readouterr()
    print("Captured Output:", captured.out)

    assert "podcast_id" in data
    assert "title" in data
    assert data["title"] == "Test Episode Title"
    assert mock_generate_script.called
    assert mock_generate_email_headers.called
