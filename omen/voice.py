from io import BytesIO
import tempfile
from pathlib import Path

_whisper_model = None

def voice_status():
    try:
        import faster_whisper  # noqa: F401
        stt = "Local speech recognition: ready (faster-whisper installed)"
    except ImportError:
        stt = "Local speech recognition: install optional voice dependencies"
    try:
        import gtts  # noqa: F401
        tts = "Online speech synthesis: ready (gTTS installed)"
    except ImportError:
        tts = "Speech synthesis: install optional voice dependencies"
    return f"{stt}\\n\\n{tts}"

def transcribe_audio(audio_bytes):
    """Transcribe Streamlit-recorded WAV audio locally with faster-whisper."""
    global _whisper_model
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Voice recognition is optional. Install it with: pip install -r requirements-voice.txt"
        ) from exc

    if _whisper_model is None:
        _whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        temp_path = tmp.name
    try:
        segments, info = _whisper_model.transcribe(temp_path, beam_size=5, vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise RuntimeError("No speech was recognized. Try recording again.")
        return text
    finally:
        Path(temp_path).unlink(missing_ok=True)

def speak_text(text):
    """Generate MP3 speech using gTTS. Requires internet; no API key is needed."""
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise RuntimeError("Install speech output with: pip install -r requirements-voice.txt") from exc
    # Auto language detection is imperfect; English is the safe default.
    audio = BytesIO()
    gTTS(text=text[:4000], lang="en").write_to_fp(audio)
    return audio.getvalue()
