import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
CLOUD_MODEL = os.getenv("CLOUD_MODEL", "gpt-4o-mini")
PROVIDER_MODE = os.getenv("OMEN_PROVIDER", "hybrid").lower()  # hybrid | local | cloud
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
WORKSPACE_DIR = os.getenv("OMEN_WORKSPACE", "workspace")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
