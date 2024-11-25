import base64
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import json
import numpy as np
from ..app import app, process_audio, detect_silence, analyze_with_gpt

client = TestClient(app)

# Mock audio data (1 second of silence)
MOCK_SILENCE_AUDIO = base64.b64encode(np.zeros(44100, dtype=np.float32).tobytes()).decode()

# Mock audio data (1 second of speech-like signal)
MOCK_SPEECH_AUDIO = base64.b64encode((np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100)) * 0.5).astype(np.float32).tobytes()).decode()

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_silence_detection():
    """Test silence detection function"""
    # Test silence
    assert detect_silence(f"data:audio/wav;base64,{MOCK_SILENCE_AUDIO}") == True
    
    # Test non-silence
    assert detect_silence(f"data:audio/wav;base64,{MOCK_SPEECH_AUDIO}") == False

@pytest.mark.asyncio
async def test_process_audio():
    """Test audio processing function"""
    # Test with speech audio
    text, success = process_audio(f"data:audio/wav;base64,{MOCK_SPEECH_AUDIO}")
    assert success == True
    assert isinstance(text, str)

    # Test with invalid audio data
    text, success = process_audio("invalid_audio_data")
    assert success == False
    assert isinstance(text, str)  # Should return error message

def test_gpt_analysis():
    """Test GPT analysis function"""
    # Test with sample text
    sample_text = "This is a test transcription for analysis"
    result = analyze_with_gpt(sample_text)
    
    assert isinstance(result, dict)
    assert "topic" in result or "error" in result
    if "topic" in result:
        assert "concerns" in result
        assert "suggestion" in result

@pytest.mark.asyncio
async def test_websocket():
    """Test WebSocket functionality"""
    async with client.websocket_connect("/ws") as websocket:
        # Test sending audio data
        data = {
            "audio": f"data:audio/wav;base64,{MOCK_SPEECH_AUDIO}"
        }
        await websocket.send_json(data)
        
        # Receive response
        response = await websocket.receive_json()
        assert "transcription" in response or "error" in response

@pytest.mark.asyncio
async def test_websocket_error():
    """Test WebSocket error handling"""
    async with client.websocket_connect("/ws") as websocket:
        # Test with invalid data
        data = {
            "audio": "invalid_data"
        }
        await websocket.send_json(data)
        
        # Should receive error response
        response = await websocket.receive_json()
        assert "error" in response
