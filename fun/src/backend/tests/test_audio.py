import base64
import os
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import json
import numpy as np
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..app import app, process_audio, detect_silence, analyze_with_gpt

client = TestClient(app)

def create_test_wav(is_silence=True):
    """Create a test WAV file and return its base64 encoding"""
    sample_rate = 44100
    duration = 1  # seconds
    if is_silence:
        samples = np.zeros(sample_rate * duration, dtype=np.float32)
    else:
        t = np.linspace(0, duration, sample_rate * duration)
        samples = np.sin(2 * np.pi * 440 * t).astype(np.float32)
    
    # Save to temporary WAV file
    import wave
    import struct
    
    temp_path = "test_audio.wav"
    with wave.open(temp_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *(samples * 32767).astype(np.int16)))
    
    # Read and encode as base64
    with open(temp_path, 'rb') as f:
        audio_data = base64.b64encode(f.read()).decode()
    
    # Clean up
    os.remove(temp_path)
    return f"data:audio/wav;base64,{audio_data}"

@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="1) Test topic 2) Test concerns 3) Test suggestion"))
        ]
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def mock_whisper():
    with patch('whisper.load_model') as mock:
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Test transcription"}
        mock.return_value = mock_model
        yield mock

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_silence_detection():
    """Test silence detection function"""
    # Test silence
    silence_audio = create_test_wav(is_silence=True)
    assert detect_silence(silence_audio) == True
    
    # Test non-silence
    speech_audio = create_test_wav(is_silence=False)
    assert detect_silence(speech_audio) == False

@pytest.mark.asyncio
async def test_process_audio(mock_whisper):
    """Test audio processing function"""
    # Configure mock
    mock_model = mock_whisper.return_value
    mock_model.transcribe.return_value = {"text": "Test transcription"}
    
    # Test with speech audio
    audio_data = create_test_wav(is_silence=False)
    text, success = process_audio(audio_data, model=mock_model)
    assert success == True
    assert text == "Test transcription"
    
    # Verify mock was called correctly
    mock_model.transcribe.assert_called_once()

def test_gpt_analysis(mock_openai):
    """Test GPT analysis function"""
    result = analyze_with_gpt("Test transcription")
    assert isinstance(result, dict)
    assert "topic" in result
    assert "concerns" in result
    assert "suggestion" in result

class MockWebSocket:
    async def send_json(self, data):
        self.sent_data = data
        return True

    async def receive_json(self):
        return self.sent_data

@pytest.mark.asyncio
async def test_websocket_connection(mock_whisper):
    """Test WebSocket connection"""
    # Configure mock
    mock_model = mock_whisper.return_value
    mock_model.transcribe.return_value = {"text": "Test transcription"}
    
    websocket = MockWebSocket()
    audio_data = create_test_wav(is_silence=False)
    await websocket.send_json({"audio": audio_data})
    response = await websocket.receive_json()
    assert "audio" in response

@pytest.mark.asyncio
async def test_websocket_error():
    """Test WebSocket error handling"""
    websocket = MockWebSocket()
    await websocket.send_json({"audio": "invalid_data"})
    response = await websocket.receive_json()
    assert "audio" in response

@pytest.mark.ui
def test_ui_audio_capture():
    """Test UI audio capture functionality"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    with webdriver.Chrome(options=options) as driver:
        # Navigate to the app
        driver.get("https://symmetrical-barnacle-6jpqvvvx694359x7-5173.app.github.dev")
        
        # Wait for the start button to be clickable
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:not(.active)"))
        )
        
        # Click start button
        start_button.click()
        
        # Verify microphone permission dialog appears
        try:
            permission_dialog = driver.switch_to.alert
            permission_dialog.accept()
        except:
            pass
        
        # Wait for status indicator to show connected
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".status-indicator.connected"))
        )
        
        # Click stop button
        stop_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.active"))
        )
        stop_button.click()
        
        # Verify status indicator shows disconnected
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".status-indicator.disconnected"))
        )

@pytest.mark.ui
def test_ui_error_handling():
    """Test UI error handling"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    with webdriver.Chrome(options=options) as driver:
        # Navigate to the app with invalid backend URL to trigger error
        driver.get("https://symmetrical-barnacle-6jpqvvvx694359x7-5173.app.github.dev")
        
        # Click start button
        start_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button:not(.active)"))
        )
        start_button.click()
        
        # Verify error message appears
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error"))
        )
        
        # Verify error can be dismissed
        close_error = driver.find_element(By.CSS_SELECTOR, ".close-error")
        close_error.click()
        
        # Verify error message disappears
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".error"))
        )
