# ◈ OMEN AI V2 — Hybrid Voice-First Agent

OMEN V2 is a voice-first personal AI agent built with Python, Streamlit, Ollama, optional OpenAI cloud fallback, Whisper speech recognition and SQLite memory.

## What it does

- **Voice input:** record audio in the browser and transcribe it locally using faster-whisper.
- **Voice output:** generate spoken responses using gTTS (internet required).
- **Hybrid AI brain:** local Ollama is primary; if it is unavailable, OMEN can fall back to the configured OpenAI API.
- **Tool use:** calculator, local date/time, persistent notes, workspace file listing and text-file reading.
- **Memory:** SQLite notes saved only when explicitly requested.
- **Multilingual:** Whisper can recognize many languages; response language depends on the selected model. TTS currently speaks English.
- **Safety:** restricted arithmetic parser, workspace path boundary, file-size limit and bounded tool-use loop.

## Architecture

```text
Browser microphone
      |
      v
Streamlit audio_input
      |
      v
faster-whisper (local speech-to-text)
      |
      v
OMEN agent loop <------> Local Ollama (primary)
      |                 Cloud OpenAI (fallback)
      v
Tool router
  |-- Calculator
  |-- Date/time
  |-- SQLite memory
  |-- Workspace file tools
      |
      v
Final text response
      |
      v
gTTS speech output (online)
```

## Requirements

- Python 3.10+
- Ollama installed and running
- A tool-capable local model, default `qwen2.5:7b`
- Optional OpenAI API key for cloud fallback
- Optional voice dependencies (faster-whisper and gTTS)

## Setup on Windows

### 1. Install and start Ollama

Install from https://ollama.com/download, then:

```powershell
ollama pull qwen2.5:7b
```

### 2. Create Python environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r requirements-voice.txt
```

The voice requirements include faster-whisper and can take time to install. If you want to test text chat first, install only `requirements.txt`.

### 3. Configure hybrid mode

Copy `.env.example` to `.env` and set your values. Environment variables are not loaded automatically by Python in this starter; either set them in PowerShell before launch or install `python-dotenv` and load the file in the app.

PowerShell example:

```powershell
$env:OMEN_PROVIDER="hybrid"
$env:OLLAMA_MODEL="qwen2.5:7b"
$env:OPENAI_API_KEY="YOUR_API_KEY"
$env:CLOUD_MODEL="gpt-4o-mini"
```

If no API key is configured, hybrid mode simply uses local Ollama. Never commit `.env` or expose API keys in GitHub.

### 4. Launch

```powershell
streamlit run app.py
```

Open http://localhost:8501.

## Provider modes

| `OMEN_PROVIDER` | Behavior |
|---|---|
| `local` | Only Ollama |
| `cloud` | Only configured OpenAI-compatible API |
| `hybrid` | Local first, cloud fallback if local is unavailable |

Cloud usage may incur API charges. A key is not included.

## Voice workflow

1. Press the browser recording control and speak.
2. Select **Transcribe recording**.
3. Review or edit the recognized text.
4. Select **Send voice message**.
5. Select **Speak last response** to hear the answer.

Speech recognition is local. Speech synthesis uses gTTS and requires internet. Current speech synthesis is English-only in this starter. Multilingual TTS and continuous wake-word listening are planned, not claimed as implemented.

## GitHub upload

```bash
git init
git add .
git commit -m "OMEN AI V2: hybrid voice-first agent"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/omen-ai-v2.git
git push -u origin main
```

## Project structure

```text
omen-ai-v2/
├── app.py
├── omen/
│   ├── __init__.py
│   ├── agent.py
│   ├── config.py
│   ├── memory.py
│   ├── tools.py
│   └── voice.py
├── workspace/
├── requirements.txt
├── requirements-voice.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

## Limitations and next milestones

- Voice input is push-to-record, not an always-listening wake-word system.
- Current TTS uses English; multilingual voice output is a future milestone.
- Hybrid routing falls back to cloud only when the local provider fails, not based on task complexity.
- No shell execution, unrestricted computer control, email sending or background autonomy.
- Next: multilingual TTS, interruption/barge-in, wake word with visible mic indicator, task planner, permission manager and action audit log.

## License

MIT.
