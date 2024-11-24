# FaithConnect Technical Specification

## Audio Format Specification
```json
{
    "aF1": {
        "format": "WAV (16-bit PCM, 44.1 kHz)",
        "reasons": [
            "Uncompressed, high-quality audio suitable for accurate transcription.",
            "Broad compatibility with transcription APIs like OpenAI Whisper API.",
            "Standard format for audio processing in Python applications."
        ],
        "official_guidelines": "WAV format compatibility verified for OpenAI Whisper API."
    }
}
```

## Audio Device Specification
```json
{
    "ad1": {
        "device": "Laptop's Built-in Microphone",
        "features": [
            "Utilized for audio input in the absence of external microphones.",
            "Provides acceptable sound capture for speech transcription in controlled environments.",
            "Integrated with Python application using the `PyAudio` library for audio recording.",
            "Supports continuous audio capture after being enabled.",
            "Allows for continuous listening until the user disables the function."
        ],
        "references": ["PyAudio library documentation"]
    }
}
```

## API Specifications

### Transcription API
```json
{
    "ta1": {
        "api": "OpenAI Whisper API",
        "features": [
            "Transcription API for converting speech to text.",
            "Cost: $0.006 per minute of audio.",
            "Supports WAV format for efficient processing.",
            "Provides accurate transcription for a variety of accents and languages.",
            "Handles continuous transcription updates as audio is captured.",
            "Detects when speakers stop talking to trigger message sending."
        ],
        "references": ["Whisper API official documentation"]
    }
}
```

### AI Processing API
```json
{
    "ai1": {
        "api": "OpenAI GPT-4o-mini with Caching",
        "features": [
            "Processes the transcription output from Whisper API.",
            "Caching Mechanism: Uses Python's `functools.lru_cache` to store results temporarily.",
            "Summarizes transcriptions, extracts actionable insights, and generates responses.",
            "Supports continuous processing of updated transcripts.",
            "Integrates with the chat screen to display updates in real-time.",
            "Analyzes client conversations for key points, concerns, and requirements.",
            "Generates suggested responses to client questions in real time.",
            "Provides analysis to help present company competencies effectively."
        ],
        "references": ["GPT-4o-mini pricing and features"]
    }
}
```

## System Architecture

```
FaithConnect
├── Audio Capture Layer
│   ├── Microphone Interface
│   └── Audio Format Converter
├── Processing Layer
│   ├── Transcription Service
│   └── AI Processing Engine
├── Caching Layer
│   ├── Local Cache
│   └── API Response Cache
├── Presentation Layer
│   ├── Web Interface
│   └── Results Display
└── Meeting Assistant Layer 
    ├── Client Analysis Module 
    └── Suggestion Generation Module
```

## Core Features

### Continuous Listening
- Voice Activity Detection (VAD) for speaker detection
- Asynchronous audio capture and processing
- Real-time transcript updates
- Silence detection (2-second threshold)
- User interface controls for enable/disable
- Real-time AI suggestions display

### Meeting Assistant
- Real-time client statement analysis
- Suggested response generation
- Client needs analysis
- Professional response formatting
- Quick response selection interface
- Privacy and security measures

### Caching System
- Local response caching using `functools.lru_cache`
- Temporary storage for transcriptions and analyses
- Retry logic for API communication
- Audio data buffering for continuous transcription

## Technical Requirements

### API Configuration
- Secure storage of OpenAI API key in environment variables
- Access via `os.environ['OPENAI_API_KEY']`
- No hardcoded API keys in application code

### Version Lock
- GPT-4o-mini exclusively
- Pre-2024 LLMs raise "Knowledge cutoff" error
- No component substitution without authorization
- Missing components trigger "Unknown Device Error"

## Workflow Process

1. User enables continuous listening
2. Audio capture via built-in microphone
3. WAV format conversion
4. Continuous Whisper API transcription
5. Real-time chat screen updates
6. Silence detection triggers message processing
7. GPT-4o-mini analysis for insights:
   - Topic and concern identification
   - Response suggestion generation
   - Summary and representation assistance
8. User interface display updates
9. Process continues until manually disabled
