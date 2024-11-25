import asyncio
import base64
import json
import logging
import numpy as np
import os
import soundfile as sf
import tempfile
import whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backend')

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
try:
    logger.info("Loading Whisper model...")
    whisper_model = whisper.load_model("base")
    logger.info("Whisper model loaded successfully")

    logger.info("Initializing OpenAI client...")
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    logger.info("OpenAI client initialized")
except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

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
        logger.info("Analyzing text with GPT")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Analyze the following text and provide: 1) Main topic 2) Key concerns 3) Suggested response"},
                {"role": "user", "content": text}
            ]
        )
        analysis = {
            "topic": response.choices[0].message.content.split("1)")[1].split("2)")[0].strip(),
            "concerns": response.choices[0].message.content.split("2)")[1].split("3)")[0].strip(),
            "suggestion": response.choices[0].message.content.split("3)")[1].strip()
        }
        logger.info("GPT analysis completed successfully")
        return analysis
    except Exception as e:
        logger.error(f"Error in GPT analysis: {str(e)}")
        return {"error": str(e)}

def save_base64_audio(audio_data: str) -> str:
    """Save base64 audio data to a temporary WAV file"""
    try:
        # Remove data URL prefix if present
        if "base64," in audio_data:
            audio_data = audio_data.split("base64,")[1]
        
        # Decode base64 data
        audio_bytes = base64.b64decode(audio_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav.write(audio_bytes)
            return temp_wav.name
    except Exception as e:
        logger.error(f"Error saving audio data: {str(e)}")
        raise

def process_audio(audio_data: str, model=None) -> Tuple[str, bool]:
    """Process audio data and return transcription"""
    try:
        logger.info("Processing audio data")
        temp_path = save_base64_audio(audio_data)
        
        # Use the provided model or default to the global whisper_model
        if model is None:
            model = whisper_model
        
        # Transcribe audio
        logger.info("Transcribing audio with Whisper")
        result = model.transcribe(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        logger.info("Audio processing completed successfully")
        return result["text"], True
    except Exception as e:
        logger.error(f"Error in audio processing: {str(e)}")
        return str(e), False

def detect_silence(audio_data: str, threshold: float = 0.1) -> bool:
    """Detect if audio chunk contains silence"""
    try:
        logger.info("Detecting silence in audio")
        temp_path = save_base64_audio(audio_data)
        
        # Read audio data
        data, _ = sf.read(temp_path)
        os.unlink(temp_path)

        # Calculate RMS value
        rms = np.sqrt(np.mean(np.square(data)))
        is_silence = rms < threshold
        
        logger.info(f"Silence detection completed: {'silence' if is_silence else 'sound'} detected")
        return is_silence
    except Exception as e:
        logger.error(f"Error in silence detection: {str(e)}")
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("New WebSocket connection established")
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_json()
            audio_data = data.get("audio")
            
            if not audio_data:
                await websocket.send_json({"error": "No audio data received"})
                continue
            
            # Check for silence
            if detect_silence(audio_data):
                logger.info("Silence detected, skipping processing")
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
                logger.info("Results sent to client successfully")
            else:
                await websocket.send_json({
                    "error": transcription
                })
                logger.error(f"Error processing audio: {transcription}")
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)
            try:
                await websocket.send_json({"error": str(e)})
            except:
                pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "whisper": bool(whisper_model),
            "openai": bool(client)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
