p01_improved = {
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
            "Integrated with Python application using the `PyAudio` library for audio recording.",
            "Supports continuous audio capture after being enabled.",
            "Allows for continuous listening until the user disables the function."
        ],
        "references": ["PyAudio library documentation"]
    },

    # Transcription API
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
    },

    # AI Processing API
    "ai1": {
        "api": "OpenAI GPT-4o-mini with Caching",
        "features": [
            "Processes the transcription output from Whisper API.",
            "Caching Mechanism: Uses Python's `functools.lru_cache` to store results temporarily and reduce redundant API calls.",
            "Summarizes transcriptions, extracts actionable insights, or generates contextual responses.",
            "Supports continuous processing of updated transcripts.",
            "Integrates with the chat screen to display updates in real-time.",
            "Analyzes client conversations to identify key points, concerns, and requirements.",
            "Generates suggested responses to client questions in real time to assist the user.",
            "Provides analysis to help the user present company competencies effectively."
        ],
        "references": ["GPT-4o-mini pricing and features"]
    },

    # Workflow Description in the Service Website
    "workflow": {
        "steps": [
            "1. User enables continuous listening via the application interface.",
            "2. `ad1` (Laptop's Built-in Microphone) captures audio continuously in real time.",
            "3. The audio is converted to `aF1` (WAV format) on the local machine for efficient local caching.",
            "4. The WAV audio stream is sent to `ta1` (OpenAI Whisper API) continuously for transcription.",
            "5. The transcription output is updated continuously and displayed on the chat screen.",
            "6. When speakers stop talking, the application detects silence and processes the accumulated message.",
            "7. The transcription output is processed through `ai1` (GPT-4o-mini) for actionable insights:",
            "   - Analyzes client's statements to identify key topics and concerns.",
            "   - Generates suggested responses or talking points for the user.",
            "   - Provides summaries to help the user represent themselves or their company effectively.",
            "8. Final output, including suggested responses and analysis, is displayed on the user's interface in a user-friendly format.",
            "9. The process continues, updating the transcript and providing new insights, until the user disables continuous listening."
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
            "Store frequently accessed transcriptions and analyses locally with a defined expiration time.",
            "Enable retry logic for API communication to handle transient errors gracefully.",
            "Implement buffering of audio data to allow for continuous transcription without overwhelming the API."
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
    },

    # Continuous Listening Feature
    "continuous_listening": {
        "description": "Enables the application to listen continuously after being enabled, send messages when speakers stop, and continuously update the transcript chat screen until disabled.",
        "implementation": [
            "Implement Voice Activity Detection (VAD) to detect when speakers start and stop talking.",
            "Use threading or asynchronous programming to handle continuous audio capture and processing without blocking the user interface.",
            "Update the chat screen in real time with the latest transcriptions.",
            "When silence is detected for a predefined duration (e.g., 2 seconds), consider the utterance complete and send the message for processing.",
            "Provide a user interface control to enable and disable continuous listening.",
            "Display AI-generated suggestions and analyses in a dedicated area of the interface for easy reference during meetings."
        ]
    },

    # Meeting Assistant Feature
    "meeting_assistant": {
        "description": "Enhances the application to function as an AI assistant during meetings, helping the user to answer client questions and analyze client statements to effectively represent the user or their company.",
        "implementation": [
            "Utilize the AI Processing API (`ai1`) to analyze transcriptions for key points, questions, and concerns raised by the client.",
            "Generate real-time suggested responses or talking points for the user to address client queries effectively.",
            "Provide analysis of the client's statements to help the user understand client needs and tailor responses accordingly.",
            "Ensure that the AI assistant's suggestions are concise, relevant, and professional.",
            "Integrate a mechanism for the user to quickly review and select suggested responses during the meeting.",
            "Implement privacy and security measures to ensure that meeting content and AI suggestions are kept confidential."
        ]
    }
}