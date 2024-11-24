import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

# We'll import our app once created
# from app.main import app

@pytest.fixture
def test_client():
    from app.main import app
    return TestClient(app)

@pytest.fixture
def sample_audio_file():
    # Create a dummy audio file for testing
    audio_data = io.BytesIO(b"dummy audio content")
    return ("test.wav", audio_data, "audio/wav")

def test_audio_upload(test_client, sample_audio_file):
    files = {"audio_file": sample_audio_file}
    response = test_client.post("/api/audio/upload", files=files)
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_audio_transcription(test_client):
    # First upload a file
    files = {"audio_file": ("test.wav", io.BytesIO(b"dummy audio content"), "audio/wav")}
    upload_response = test_client.post("/api/audio/upload", files=files)
    file_id = upload_response.json()["file_id"]
    
    # Then request transcription
    response = test_client.post(f"/api/audio/transcribe/{file_id}")
    assert response.status_code == 200
    assert "transcription" in response.json()
