import pyaudio
import wave
import threading
import time
from typing import Optional
import numpy as np

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
        
    def start_recording(self):
        """Start recording audio from the microphone"""
        self.recording = True
        self.frames = []
        threading.Thread(target=self._record).start()
        
    def stop_recording(self):
        """Stop recording audio"""
        self.recording = False
        
    def _record(self):
        """Internal method to handle the recording process"""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        while self.recording:
            data = stream.read(self.chunk)
            self.frames.append(data)
            
            # Check for silence
            audio_data = np.frombuffer(data, dtype=np.float32)
            if np.abs(audio_data).mean() > self.silence_threshold:
                self.last_sound_time = time.time()
                
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
    def save_wav(self, filename: str) -> Optional[str]:
        """Save recorded audio to WAV file"""
        if not self.frames:
            return None
            
        audio = pyaudio.PyAudio()
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        audio.terminate()
        return filename
        
    def is_silence_detected(self) -> bool:
        """Check if silence has been detected for the threshold duration"""
        return time.time() - self.last_sound_time > self.silence_duration
