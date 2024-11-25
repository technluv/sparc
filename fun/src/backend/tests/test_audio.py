import pytest
from fastapi.testclient import TestClient
from ..app import app

client = TestClient(app)

def test_audio_upload_endpoint():
    """Test that audio upload endpoint exists and accepts POST requests"""
    with open("tests/fixtures/test_audio.wav", "rb") as f:
        response = client.post("/api/audio/upload", files={"file": f})
    assert response.status_code == 200
    assert "id" in response.json()

def test_audio_transcription():
    """Test audio transcription functionality"""
    with open("tests/fixtures/test_audio.wav", "rb") as f:
        upload_response = client.post("/api/audio/upload", files={"file": f})
        audio_id = upload_response.json()["id"]
        
        transcribe_response = client.get(f"/api/audio/{audio_id}/transcribe")
        assert transcribe_response.status_code == 200
        assert "text" in transcribe_response.json()
