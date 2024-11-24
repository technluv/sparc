import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import json
from datetime import datetime
import asyncio
import uuid
from services.audio_service import AudioService
from services.transcription_service import TranscriptionService, AIProcessingService
from services.security_service import SecurityService
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS - updated origins to include all development ports
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Vite alternate
    "http://localhost:5175",  # Current port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

# Add CORS middleware before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory if it doesn't exist
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

# Initialize services
audio_service = AudioService()
transcription_service = TranscriptionService()
ai_service = AIProcessingService()
security_service = SecurityService()

class UserConsent(BaseModel):
    allow_recording: bool
    allow_transcription: bool
    allow_ai_processing: bool
    allow_data_retention: bool
    data_retention_period: int  # in days

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = {
            'connected_at': datetime.utcnow(),
            'consent': None
        }

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        self.user_sessions.pop(user_id, None)

    async def broadcast(self, message: str):
        disconnected = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(user_id)
        
        # Clean up disconnected clients
        for user_id in disconnected:
            self.disconnect(user_id)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "FaithConnect API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "audio_device": audio_service.get_status(),
        "security": "enabled",
        "privacy_features": ["encryption", "anonymization", "consent_management"]
    }

@app.post("/consent/{user_id}")
async def update_consent(user_id: str, consent: UserConsent):
    """Update user's privacy and consent preferences"""
    try:
        security_service.set_user_consent(user_id, consent.dict())
        security_service.create_audit_log(
            'update_consent',
            user_id,
            {'consent': consent.dict()}
        )
        return {"status": "success", "message": "Consent preferences updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = str(uuid.uuid4())  # Generate unique user ID
    await manager.connect(websocket, user_id)
    
    try:
        # Send initial connection status and audio device status
        status = audio_service.get_status()
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": "Connected to server",
            "audio_status": status,
            "user_id": user_id,
            "requires_consent": True
        }))
        
        while True:
            try:
                data = await websocket.receive_text()
                command = json.loads(data)
                
                if command["action"] == "set_consent":
                    consent_data = command.get("consent", {})
                    security_service.set_user_consent(user_id, consent_data)
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "message": "Consent preferences updated"
                    }))
                
                elif command["action"] == "start_recording":
                    # Check user consent
                    consent = security_service.get_user_consent(user_id)
                    if not consent or not consent.get('preferences', {}).get('allow_recording', False):
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "Recording consent not provided"
                        }))
                        continue

                    if not audio_service.audio_device_available:
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": "No audio device available"
                        }))
                        continue
                        
                    if audio_service.start_recording(user_id, consent.get('preferences', {})):
                        await manager.broadcast(json.dumps({
                            "type": "status",
                            "message": "Recording started"
                        }))
                        
                        # Start processing loop
                        while audio_service.recording:
                            if audio_service.is_silence_detected():
                                # Save current audio segment
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = os.path.join(TEMP_DIR, f"temp_audio_{timestamp}.wav")
                                saved_file = audio_service.save_wav(filename)
                                
                                if saved_file:
                                    # Transcribe audio
                                    transcript = await transcription_service.transcribe_audio(saved_file, user_id)
                                    if transcript:
                                        # Process with AI
                                        analysis = await ai_service.process_transcript(transcript, user_id)
                                        
                                        # Send results to client
                                        await manager.broadcast(json.dumps({
                                            "type": "analysis",
                                            "transcript": transcript,
                                            "analysis": analysis
                                        }))
                                        
                                        # Clean up temp file
                                        os.remove(saved_file)
                                        
                                # Reset for next segment
                                audio_service.frames = []
                                
                            await asyncio.sleep(0.1)
                    else:
                        await manager.broadcast(json.dumps({
                            "type": "error",
                            "message": "Failed to start recording"
                        }))
                        
                elif command["action"] == "stop_recording":
                    audio_service.stop_recording()
                    await manager.broadcast(json.dumps({
                        "type": "status",
                        "message": "Recording stopped"
                    }))
                    
                elif command["action"] == "get_status":
                    status = audio_service.get_status()
                    await websocket.send_text(json.dumps({
                        "type": "status",
                        "audio_status": status
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        audio_service.stop_recording()
        security_service.create_audit_log(
            'user_disconnect',
            user_id,
            {'reason': 'WebSocket disconnected'}
        )
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
        manager.disconnect(user_id)
        audio_service.stop_recording()
        security_service.create_audit_log(
            'error',
            user_id,
            {'error': str(e)}
        )
