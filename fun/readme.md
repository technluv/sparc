# Real-time Audio Analysis System

A real-time audio transcription and analysis system that captures audio from your browser's microphone, transcribes it using Whisper API, and provides insights using GPT-4.

## Features

1. Continuous Audio Listening
   - Browser-based audio capture
   - Real-time streaming via WebSocket
   - Automatic silence detection

2. Audio Processing
   - WAV format conversion
   - Noise suppression
   - Echo cancellation

3. Transcription & Analysis
   - Real-time Whisper API transcription
   - GPT-4 analysis for:
     - Topic identification
     - Key concerns detection
     - Response suggestions

4. User Interface
   - Real-time status updates
   - Live transcription display
   - Debug panel for monitoring
   - Error handling and recovery

## Requirements

- Python 3.8 or higher
- Node.js 14 or higher
- npm 6 or higher
- ffmpeg
- Chrome/Chromium (for UI tests)

## Installation

1. Install ffmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows (using Chocolatey)
   choco install ffmpeg
   ```

2. Install Chrome/Chromium for UI tests:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install chromium-browser

   # macOS
   brew install --cask chromium

   # Windows (using Chocolatey)
   choco install chromium
   ```

3. Run the start script:
   ```bash
   ./start.sh
   ```

The script will:
- Set up Python virtual environment
- Install backend dependencies
- Run backend tests (including UI tests)
- Install frontend dependencies
- Start both servers

## Usage

1. Access the application at:
   ```
   https://symmetrical-barnacle-6jpqvvvx694359x7-5173.app.github.dev
   ```
   Note: The exact URL will be provided in your terminal when running the frontend server.

2. Click "Start Listening" to begin audio capture
3. Speak into your microphone
4. Watch real-time transcriptions and analysis appear
5. Use the debug panel to monitor system status
6. Click "Stop Listening" to end the session

## Architecture

### Backend (FastAPI)
- WebSocket server for real-time communication
- Audio processing pipeline
- Integration with Whisper API for transcription
- Integration with GPT-4 for analysis
- Error handling and recovery

### Frontend (React)
- Browser audio capture using MediaRecorder API
- WebSocket client for real-time updates
- Real-time UI updates
- Debug panel for monitoring
- Error display and handling

## Development

### Backend
```bash
cd src/backend
source venv/bin/activate
uvicorn app:app --reload
```

### Frontend
```bash
cd src/frontend
npm install
npm run dev
```

## Testing

### Backend Tests
```bash
cd src/backend
python -m pytest
```

### UI Tests
```bash
cd src/backend
python -m pytest -m ui
```

The UI tests verify:
- Audio capture functionality
- Microphone permissions
- Connection status indicators
- Error handling
- User interface interactions

## Troubleshooting

1. Microphone Access
   - Ensure your browser has permission to access the microphone
   - Check browser console for any permission errors

2. Audio Issues
   - Verify microphone is working in system settings
   - Check audio input levels
   - Ensure no other applications are using the microphone

3. Connection Issues
   - Check if backend server is running (http://localhost:8000/health)
   - Verify WebSocket connection in browser console
   - Check debug panel for connection status

4. API Issues
   - Verify OPENAI_API_KEY is set correctly
   - Check debug panel for API errors
   - Verify internet connection

5. UI Test Issues
   - Ensure Chrome/Chromium is installed
   - Check if the correct URL is being used in tests
   - Verify WebDriver is properly configured

## License

MIT License - see LICENSE file for details
