p01 = {
    # Possible Audio Format
    "aF1": {
        "format": "WAV (16-bit PCM, 44.1 kHz)",
        "reasons": [
            "Uncompressed, high-quality audio suitable for accurate transcription.",
            "Broad compatibility with transcription APIs like OpenAI Whisper API.",
            "Standard format for audio processing in Python applications."
        ],
        "official_guidelines": "WAV format compatibility verified for OpenAI Whisper API."
    },

    # Example Audio Device
    "ad1": {
        "device": "Laptop's Built-in Microphone",
        "features": [
            "Utilized for audio input in the absence of external microphones.",
            "Provides acceptable sound capture for speech transcription in controlled environments.",
            "Integrated with Python application using the `pyaudio` library for audio recording."
        ],
        "references": ["pyaudio library documentation"]
    },

    # Transcription API
    "ta1": {
        "api": "OpenAI Whisper API",
        "features": [
            "Transcription API for converting speech to text.",
            "Cost: $0.006 per minute of audio.",
            "Supports WAV format for efficient processing.",
            "Provides accurate transcription for a variety of accents and languages."
        ],
        "references": ["Whisper API official documentation"]
    },

    # AI Processing API
    "ai1": {
        "api": "OpenAI GPT-4o-mini with Caching",
        "features": [
            "Processes the transcription output from Whisper API.",
            "Caching Mechanism: Uses Python's `functools.lru_cache` to store results temporarily and reduce redundant API calls.",
            "Summarizes transcriptions, extracts actionable insights, or generates contextual responses."
        ],
        "references": ["GPT-4o-mini pricing and features"]
    },

    # Workflow Description in the Service Website
    "workflow": {
        "steps": [
            "1. `ad1` (Laptop's Built-in Microphone) captures audio in real time.",
            "2. The audio is converted to `aF1` (WAV format) on the local machine for efficient local caching.",
            "3. The WAV audio file is sent to `ta1` (OpenAI Whisper API) for transcription.",
            "4. The transcription output is processed through `ai1` (GPT-4o-mini) for actionable insights.",
            "5. Final output is displayed on the web interface in a user-friendly format."
        ]
    },

    # Lock on Facts and Technology as of today=(November 24, 2024)
    "lock": {
        "mandatory_adherence": [
            "Use GPT-4o-mini exclusively. Do not switch to GPT-4 or other models unless explicitly authorized.",
            "Old LLMs with pre-2024 knowledge cutoff must raise the error: 'Knowledge cutoff: Unable to confirm 2024 requirements.'",
            "Substituting components (e.g., microphones, APIs) is not allowed. Missing components must result in an 'Unknown Device Error.'"
        ]
    },

    # Caching Mechanism for OpenAI APIs
    "caching": {
        "description": "Implement caching to optimize API usage and reduce costs.",
        "implementation": [
            "Use `functools.lru_cache` for caching responses from the GPT-4o-mini model.",
            "Store frequently accessed transcriptions locally with a defined expiration time.",
            "Enable retry logic for API communication to handle transient errors gracefully."
        ]
    },

    # API Key Configuration
    "api_configuration": {
        "OPENAI_API_KEY": {
            "description": "The OpenAI API key must be securely stored as an environment variable.",
            "implementation": [
                "In Code Spaces, set the `OPENAI_API_KEY` environment variable using the Secrets Manager.",
                "Access the API key in the Python code using `os.environ['OPENAI_API_KEY']`.",
                "Ensure the API key is not hardcoded in the application for security."
            ]
        }
    }
}
