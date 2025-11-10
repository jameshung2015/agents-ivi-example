import os
from dotenv import load_dotenv

load_dotenv()

AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "ollama/deepseek-v3.1:671b-cloud")

if not OLLAMA_BASE_URL:
    raise ValueError("OLLAMA_BASE_URL is required")
