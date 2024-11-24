import os
from functools import lru_cache
import openai
from typing import Optional

class TranscriptionService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
    @lru_cache(maxsize=100)
    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using OpenAI Whisper API
        Uses caching to avoid re-transcribing identical audio segments
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                response = await openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                return response
        except Exception as e:
            print(f"Error in transcription: {str(e)}")
            return None

class AIProcessingService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
    @lru_cache(maxsize=100)
    async def process_transcript(self, transcript: str) -> dict:
        """
        Process transcribed text using GPT-4o-mini
        Returns analysis including key points, concerns, and suggested responses
        Uses caching to avoid reprocessing identical transcripts
        """
        try:
            system_prompt = """
            You are an AI assistant analyzing client conversations. Identify:
            1. Key topics and concerns
            2. Suggested professional responses
            3. Important insights for effective communication
            Format the response as a structured JSON.
            """
            
            response = await openai.chat.completions.create(
                model="gpt-4",  # Using GPT-4 as specified
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript}
                ],
                temperature=0.7
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "timestamp": response.created
            }
            
        except Exception as e:
            print(f"Error in AI processing: {str(e)}")
            return {
                "error": str(e),
                "analysis": None
            }
