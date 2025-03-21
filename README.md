# Smart Meeting Assistant

A web application that transcribes audio files and generates meeting minutes using AI. Built with Flask and Whisper.

## Features

- Audio file transcription using OpenAI's Whisper
- AI-powered meeting minutes generation using Groq
- Modern, responsive dark-themed UI
- Meeting history management
- Download functionality for meeting minutes
- Support for various audio formats

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio processing)
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-meeting-assistant.git
cd smart-meeting-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Upload an audio file and click "Process Audio"

4. View the transcription and AI-generated meeting minutes

5. Download the results or view them in the meeting history

## Supported Audio Formats

- WAV
- MP3
- M4A
- OGG
- FLAC
- AAC
- WMA
- AIFF
- ALAC
- PCM
- And more...

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 