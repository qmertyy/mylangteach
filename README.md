#  Language Teacher

A hobby project I have developed to help me learn German.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![SvelteKit](https://img.shields.io/badge/svelte-4-orange)

##  Features

###  Free Talk Mode
- Natural conversations on any topic
- Automatic grammar detection and suggestions
- Voice input with local transcription
- Topic suggestions to get started

###  Grammar Mode  
- Focused lessons on specific grammar rules
- Explanations with examples
- Practice exercises
- Progress tracking per grammar topic

###  Document Mode
- Upload PDFs, images, or text files
- Automatic vocabulary extraction
- Conversational learning from document content
- Sentence structure practice

###  Voice Input 
- Record audio messages with your microphone
- Local speech-to-text using faster-whisper (no API key needed)
- Automatic transcription and sending
- Works in all chat modes

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- [Ollama](https://ollama.ai/) (for local LLM)

### Installation

**1. Clone and setup backend:**
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

**2. Setup frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**3. Setup Ollama:**
```bash
# Install from https://ollama.ai/download
# Then pull a model:
ollama pull llama3.2
```

**4. Open the app:**
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs

## 🎤 Voice Input Setup

Voice input uses **faster-whisper** which runs locally. The first time you use it, it will download the Whisper model (~150MB for "base" model).

No additional setup needed! Just click the microphone button and start talking.






##  API Endpoints

### Config
- `GET /api/config` - Get LLM & Whisper configuration
- `POST /api/config` - Update LLM configuration
- `POST /api/config/whisper` - Update Whisper configuration

### Chats
- `GET /api/chats` - List chats (filter by mode/category)
- `POST /api/chats` - Create chat
- `GET /api/chats/{id}` - Get chat with messages
- `DELETE /api/chats/{id}` - Delete chat
- `POST /api/chats/{id}/messages` - Send message

### Audio
- `POST /api/audio/transcribe` - Transcribe audio to text
- `POST /api/audio/transcribe-and-send` - Transcribe & send as message
- `GET /api/audio/formats` - Get supported formats

### Documents
- `GET /api/documents` - List documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category
- `DELETE /api/categories/{id}` - Delete category

### Grammar Rules
- `GET /api/grammar-rules` - List learned rules
- `POST /api/grammar-rules` - Create rule + chat
- `DELETE /api/grammar-rules/{id}` - Delete rule


## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [SvelteKit](https://kit.svelte.dev/) - Frontend framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Speech-to-text
- [Tailwind CSS](https://tailwindcss.com/) - Styling
