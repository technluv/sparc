import asyncio
import base64
import json
import numpy as np
import os
import soundfile as sf
import tempfile
import whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import wave

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Whisper model
whisper_model = whisper.load_model("base")

# Initialize OpenAI client
client = OpenAI()

class AudioData(BaseModel):
    audio: str  # Base64 encoded audio data

class TranscriptionResult(BaseModel):
    text: str
    analysis: dict

# Store active WebSocket connections
active_connections: List[WebSocket] = []

def analyze_with_gpt(text: str) -> dict:
    """Analyze transcribed text with GPT-4"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the following text and provide: 1) Main topic 2) Key concerns 3) Suggested response"},
                {"role": "user", "content": text}
            ]
        )
        return {
            "topic": response.choices[0].message.content.split("1)")[1].split("2)")[0].strip(),
            "concerns": response.choices[0].message.content.split("2)")[1].split("3)")[0].strip(),
            "suggestion": response.choices[0].message.content.split("3)")[1].strip()
        }
    except Exception as e:
        return {"error": str(e)}

def process_audio(audio_data: str) -> tuple:
    """Process base64 audio data to WAV format and transcribe"""
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav.write(audio_bytes)
            temp_wav_path = temp_wav.name

        # Transcribe audio using Whisper
        result = whisper_model.transcribe(temp_wav_path)
        
        # Clean up temporary file
        os.unlink(temp_wav_path)
        
        return result["text"], True
    except Exception as e:
        return str(e), False

def detect_silence(audio_data: str, threshold: float = 0.1) -> bool:
    """Detect if audio chunk contains silence"""
    try:
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav.write(audio_bytes)
            temp_wav_path = temp_wav.name

        # Read audio data
        data, _ = sf.read(temp_wav_path)
        os.unlink(temp_wav_path)

        # Calculate RMS value
        rms = np.sqrt(np.mean(np.square(data)))
        return rms < threshold
    except Exception:
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_json()
            audio_data = data.get("audio")
            
            # Check for silence
            if detect_silence(audio_data):
                continue
                
            # Process audio
            transcription, success = process_audio(audio_data)
            
            if success:
                # Analyze with GPT
                analysis = analyze_with_gpt(transcription)
                
                # Send results back to client
                await websocket.send_json({
                    "transcription": transcription,
                    "analysis": analysis
                })
            else:
                await websocket.send_json({
                    "error": transcription
                })
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        active_connections.remove(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
