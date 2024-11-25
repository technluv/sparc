from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uuid

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/audio/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Handle audio file upload"""
    file_id = str(uuid.uuid4())
    # TODO: Implement file storage
    return {"id": file_id}

@app.get("/api/audio/{audio_id}/transcribe")
async def transcribe_audio(audio_id: str):
    """Transcribe audio file"""
    # TODO: Implement transcription
    return {"text": "Sample transcription"}
