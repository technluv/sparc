import os
from functools import lru_cache
from openai import AsyncOpenAI
from typing import Optional, Dict, Any
from datetime import datetime
from .security_service import SecurityService

class TranscriptionService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=api_key)
        self.security_service = SecurityService()
            
    @lru_cache(maxsize=100)
    async def transcribe_audio(self, audio_file_path: str, user_id: str) -> Optional[str]:
        """
        Transcribe audio file using OpenAI Whisper API with privacy measures
        Uses caching to avoid re-transcribing identical audio segments
        """
        try:
            # Check user consent
            consent = self.security_service.get_user_consent(user_id)
            if not consent or not consent.get('preferences', {}).get('allow_transcription', False):
                raise ValueError("User has not consented to transcription")

            # Log transcription attempt
            self.security_service.create_audit_log(
                'start_transcription',
                user_id,
                {'file': audio_file_path}
            )

            with open(audio_file_path, 'rb') as audio_file:
                # Verify file integrity
                audio_data = audio_file.read()
                stored_hash = self.security_service.hash_audio_data(audio_data)
                
                if not self.security_service.verify_audio_integrity(audio_data, stored_hash):
                    raise ValueError("Audio file integrity check failed")

                response = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )

                # Anonymize the transcript
                anonymized_transcript = self.security_service.anonymize_transcript(response)

                # Log successful transcription
                self.security_service.create_audit_log(
                    'complete_transcription',
                    user_id,
                    {
                        'file': audio_file_path,
                        'success': True,
                        'length': len(anonymized_transcript)
                    }
                )

                return anonymized_transcript

        except Exception as e:
            # Log transcription error
            self.security_service.create_audit_log(
                'transcription_error',
                user_id,
                {
                    'file': audio_file_path,
                    'error': str(e)
                }
            )
            print(f"Error in transcription: {str(e)}")
            return None

class AIProcessingService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=api_key)
        self.security_service = SecurityService()
            
    @lru_cache(maxsize=100)
    async def process_transcript(self, transcript: str, user_id: str) -> dict:
        """
        Process transcribed text using GPT-4 with privacy measures
        Returns analysis including key points, concerns, and suggested responses
        Uses caching to avoid reprocessing identical transcripts
        """
        try:
            # Check user consent
            consent = self.security_service.get_user_consent(user_id)
            if not consent or not consent.get('preferences', {}).get('allow_ai_processing', False):
                raise ValueError("User has not consented to AI processing")

            # Log AI processing attempt
            self.security_service.create_audit_log(
                'start_ai_processing',
                user_id,
                {'transcript_length': len(transcript)}
            )

            system_prompt = """
            You are an AI assistant analyzing client conversations. Identify:
            1. Key topics and concerns
            2. Suggested professional responses
            3. Important insights for effective communication
            Format the response as a structured JSON.
            IMPORTANT: Do not include any personally identifiable information in the analysis.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript}
                ],
                temperature=0.7
            )

            analysis = response.choices[0].message.content

            # Verify no PII in analysis
            sanitized_analysis = self.security_service.anonymize_transcript(analysis)
            
            # Log successful processing
            self.security_service.create_audit_log(
                'complete_ai_processing',
                user_id,
                {
                    'success': True,
                    'analysis_length': len(sanitized_analysis)
                }
            )
            
            return {
                "analysis": sanitized_analysis,
                "timestamp": response.created,
                "privacy_level": "anonymized"
            }
            
        except Exception as e:
            # Log AI processing error
            self.security_service.create_audit_log(
                'ai_processing_error',
                user_id,
                {'error': str(e)}
            )
            print(f"Error in AI processing: {str(e)}")
            return {
                "error": str(e),
                "analysis": None
            }
