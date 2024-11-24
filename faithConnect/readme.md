# Installation Instructions

## Prerequisites

Ensure you have the following installed on your system:

- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- [Git](https://git-scm.com/downloads) (version 2.20 or higher)
- [OpenAI API Key](https://platform.openai.com/api-keys)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) (for audio capture)

## Clone the Repository

```bash
git clone https://github.com/yourusername/faithConnect.git
cd faithConnect
```

## Set Up Environment Variables

1. Create a `.env` file in the project root:

    ```bash
    touch .env
    ```

2. Add your OpenAI API key to the `.env` file:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

## Install Dependencies

1. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

2. Install required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Run the Application

1. Start the application:

    ```bash
    python src/main.py
    ```

2. Open your web browser and navigate to:

    ```
    http://localhost:3000
    ```

## Features

- Real-time audio capture and transcription
- AI-powered meeting assistance
- Continuous listening with automatic message detection
- Client conversation analysis
- Suggested response generation
- Local caching for optimized performance

## Running Tests

Execute the test suite:

```bash
python -m pytest tests/
```

## Troubleshooting

- **Audio Capture Issues:**
  - Ensure your microphone is properly connected and configured
  - Check PyAudio installation if you encounter audio-related errors
  
- **API Connection Issues:**
  - Verify your OpenAI API key is correctly set in the `.env` file
  - Check your internet connection
  - Ensure you have sufficient API credits

- **Performance Issues:**
  - Clear the local cache if the application becomes slow
  - Restart the application if real-time updates are delayed

## Contributing

Please refer to the project's contribution guidelines for information on how to contribute to this project.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
