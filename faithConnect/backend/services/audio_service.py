import pyaudio
import wave
import threading
import time
from typing import Optional, Dict, Any
import numpy as np
import os
from datetime import datetime
from .security_service import SecurityService

class AudioService:
    def __init__(self):
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.recording = False
        self.frames = []
        self.silence_threshold = 0.01
        self.silence_duration = 2  # seconds
        self.last_sound_time = time.time()
        self.audio_device_available = self._check_audio_device()
        self.security_service = SecurityService()
        self.current_session: Optional[Dict[str, Any]] = None
        
    def _check_audio_device(self) -> bool:
        """Check if any audio input device is available"""
        try:
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            audio.terminate()
            return device_count > 0
        except:
            return False
        
    def start_recording(self, user_id: str, consent_data: Dict[str, bool]) -> bool:
        """Start recording audio from the microphone"""
        if not self.audio_device_available:
            return False
            
        # Store user consent
        self.security_service.set_user_consent(user_id, consent_data)
        
        # Create new session
        self.current_session = {
            'user_id': user_id,
            'start_time': datetime.utcnow(),
            'device_id': self._get_device_id(),
            'consent_version': '1.0'
        }
        
        # Log session start
        self.security_service.create_audit_log(
            'start_recording',
            user_id,
            {'session_id': id(self.current_session)}
        )
            
        self.recording = True
        self.frames = []
        threading.Thread(target=self._record).start()
        return True
        
    def stop_recording(self):
        """Stop recording audio"""
        if self.current_session:
            self.security_service.create_audit_log(
                'stop_recording',
                self.current_session['user_id'],
                {'session_id': id(self.current_session)}
            )
        self.recording = False
        self.current_session = None
        
    def _get_device_id(self) -> str:
        """Get unique identifier for current audio device"""
        try:
            audio = pyaudio.PyAudio()
            device_info = audio.get_default_input_device_info()
            audio.terminate()
            return str(device_info.get('index', 'unknown'))
        except:
            return 'unknown'
        
    def _record(self):
        """Internal method to handle the recording process"""
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while self.recording:
                try:
                    data = stream.read(self.chunk)
                    # Encrypt audio chunk before storing
                    encrypted_data = self.security_service.encrypt_audio_data(data)
                    self.frames.append(encrypted_data)
                    
                    # Check for silence
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    if np.abs(audio_data).mean() > self.silence_threshold:
                        self.last_sound_time = time.time()
                except IOError as e:
                    # Handle audio stream errors
                    print(f"Audio stream error: {str(e)}")
                    break
                    
            stream.stop_stream()
            stream.close()
            audio.terminate()
        except Exception as e:
            print(f"Recording error: {str(e)}")
            self.recording = False
        
    def save_wav(self, original_filename: str) -> Optional[str]:
        """Save recorded audio to WAV file with security measures"""
        if not self.frames or not self.current_session:
            return None
            
        try:
            # Generate secure filename
            filename = self.security_service.generate_secure_filename(original_filename)
            
            # Create metadata
            metadata = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': self.current_session['user_id'],
                'device_id': self.current_session['device_id'],
                'sample_rate': self.rate,
                'channels': self.channels,
                'format': str(self.format)
            }
            
            # Sanitize metadata
            safe_metadata = self.security_service.sanitize_metadata(metadata)
            
            # Decrypt frames for saving
            decrypted_frames = []
            for frame in self.frames:
                try:
                    decrypted_frame = self.security_service.decrypt_audio_data(frame)
                    decrypted_frames.append(decrypted_frame)
                except Exception as e:
                    print(f"Error decrypting frame: {str(e)}")
                    continue
            
            audio = pyaudio.PyAudio()
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(decrypted_frames))
            audio.terminate()
            
            # Calculate hash for integrity verification
            audio_hash = self.security_service.hash_audio_data(b''.join(decrypted_frames))
            
            # Log file creation
            self.security_service.create_audit_log(
                'save_audio',
                self.current_session['user_id'],
                {
                    'filename': filename,
                    'hash': audio_hash,
                    'metadata': safe_metadata
                }
            )
            
            return filename
        except Exception as e:
            print(f"Error saving WAV file: {str(e)}")
            return None
        
    def is_silence_detected(self) -> bool:
        """Check if silence has been detected for the threshold duration"""
        return time.time() - self.last_sound_time > self.silence_duration
        
    def get_status(self) -> dict:
        """Get the current status of the audio service"""
        status = {
            "audio_device_available": self.audio_device_available,
            "is_recording": self.recording,
            "has_audio_data": len(self.frames) > 0
        }
        
        if self.current_session:
            status.update({
                "session_active": True,
                "session_start": self.current_session['start_time'].isoformat(),
                "privacy_enabled": self.security_service.get_user_consent(
                    self.current_session['user_id']
                )
            })
            
        return status
