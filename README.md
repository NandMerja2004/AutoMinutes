# 🎬 AutoMinutes

> **Turn recordings into decisions.**  
> Automatically transcribe, summarize, and extract actionable insights from YouTube videos and local audio/video files, with an interactive RAG chat to query meeting transcripts.

---

## 🌟 Overview

**AutoMinutes** is an AI-powered meeting intelligence system built with Streamlit, Whisper, LangChain, and Mistral AI. It ingests video and audio content, transcribes spoken speech into text, extracts high-value structured takeaways, and indexes the transcript into a local vector database for grounded question answering.

---

## ✨ Features

- **Multi-Source Ingestion**:
  - Direct YouTube URL downloads via `yt-dlp`.
  - Local file uploads supporting `.mp3`, `.wav`, `.m4a`, `.mp4`, `.mkv`, `.webm`, and `.mov`.
- **Accurate Speech-to-Text**:
  - Local transcription powered by OpenAI Whisper (`openai-whisper`).
  - Automatic chunking and preprocessing with `pydub` and `ffmpeg`.
- **Intelligent Information Extraction**:
  - **Auto Title**: Generates clean, descriptive meeting titles.
  - **Executive Summary**: Synthesizes the core discussion.
  - **Action Items**: Interactive checklist to track deliverables and ownership.
  - **Key Decisions**: Pinpoints consensus items and formal decisions.
  - **Open Questions**: Highlights unresolved discussion points.
- **RAG-Powered Chat**:
  - In-memory/local vector indexing with `chromadb` and `sentence-transformers`.
  - Chat with your meeting transcript to locate specific topics and speaker context.
- **Export & History**:
  - Export analysis directly to `.docx` (Word) or `.pdf`.
  - Local history tracking and persistent session management.
  - One-click copy buttons for clean text extraction.
- **Modern Glassmorphism UI**:
  - Custom dark-mode Streamlit interface with live progress tracking and cancelable pipelines.

---

## 🏗️ Architecture & Pipeline

```text
[ YouTube URL / Local Audio/Video ]
               │
               ▼
     [ utils.audio_processor ]
        (Download & Chunking)
               │
               ▼
      [ core.transcriber ]
        (Whisper STT Model)
               │
               ▼
       Meeting Transcript
         │           │
         ▼           ▼
[ core.summarizer ] [ core.rag_engine ]
[ core.extractor  ]   (ChromaDB + Mistral Embeddings/LLM)
  • Summary             │
  • Action Items        ▼
  • Key Decisions     Interactive Q&A Chat
  • Open Questions
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python**: Version `3.10` or higher recommended.
- **FFmpeg**: Must be installed on your system and available in your system `PATH`.
  - **macOS** (Homebrew): `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
  - **Windows** (Chocolatey): `choco install ffmpeg` (or download from [ffmpeg.org](https://ffmpeg.org/))

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/autominutes.git
cd autominutes
```

### 3. Set Up a Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate on Linux/macOS:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

*(Optional: If you want `.docx` export support, verify `python-docx` is installed: `pip install python-docx`)*

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# Mistral AI API key for summarization and RAG chat
MISTRAL_API_KEY="your-mistral-api-key-here"

# (Optional) Sarvam AI or custom keys if using Hinglish translation
SARVAM_API_KEY="your-sarvam-api-key"
```

---

## 💻 Usage

### Web Interface (Streamlit)

Launch the glassmorphism Streamlit UI:

```bash
streamlit run app.py
```

1. Open your browser at `http://localhost:8501`.
2. Paste a YouTube URL or upload an audio/video file.
3. Click **Start Analysis**.
4. View real-time progress, browse summaries, tick off action items, export reports, and chat with the transcript.

### Command Line Interface (CLI)

You can also run the full pipeline in terminal mode via `main.py`:

```bash
python main.py
```

Follow the prompt to provide a YouTube URL or path to a local media file. Once complete, you can chat with the meeting directly in your terminal.

---

## 📁 Project Structure

```text
├── app.py                   # Streamlit web application & UI
├── main.py                  # CLI entry point and pipeline orchestrator
├── test.py                  # Standalone test script for transcription/summarization
├── requirements.txt         # Project dependencies
├── core/
│   ├── transcriber.py       # Whisper speech-to-text integration
│   ├── summarizer.py        # Title and summary generation
│   ├── extractor.py         # Action items, key decisions, open questions
│   └── rag_engine.py        # Vector store indexer & Q&A chain
├── utils/
│   └── audio_processor.py   # Audio download (yt-dlp) & splitting (pydub)
└── data/                    # Auto-generated runtime storage (uploads & history)
    ├── history/             # Saved analyses (.json)
    └── uploads/             # Temporary uploaded audio/video files
```

---

## 🛠️️ Troubleshooting

- **`ffmpeg wasn't found`**: Ensure `ffmpeg` and `ffprobe` are installed and added to your system `PATH`. Run `ffmpeg -version` in your terminal to verify.
- **`yt-dlp download errors`**: YouTube frequently updates its player APIs. Upgrade `yt-dlp` to the latest release:
  ```bash
  pip install --upgrade yt-dlp
  ```
- **Out of Memory during Transcription**: By default, Whisper models can require significant RAM/VRAM. You can configure smaller models (e.g., `tiny` or `base`) inside `core/transcriber.py`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).