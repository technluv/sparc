import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from datetime import datetime
import asyncio
from services.audio_service import AudioService
from services.transcription_service import TranscriptionService, AIProcessingService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "FaithConnect API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            command = json.loads(data)
            
            if command["action"] == "start_recording":
                audio_service.start_recording()
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
                            transcript = await transcription_service.transcribe_audio(saved_file)
                            if transcript:
                                # Process with AI
                                analysis = await ai_service.process_transcript(transcript)
                                
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
                    
            elif command["action"] == "stop_recording":
                audio_service.stop_recording()
                await manager.broadcast(json.dumps({
                    "type": "status",
                    "message": "Recording stopped"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        audio_service.stop_recording()
