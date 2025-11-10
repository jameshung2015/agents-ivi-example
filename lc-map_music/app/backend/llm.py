"""
LLM 配置模块 - 使用 LangChain 1.0 推荐的 Ollama 集成
"""
import logging
from langchain_ollama import ChatOllama
from .config import OLLAMA_BASE_URL, LLM_MODEL

# 配置日志
logger = logging.getLogger(__name__)

# 从 "ollama/model_name" 格式中提取模型名
model_name = LLM_MODEL.replace("ollama/", "") if LLM_MODEL.startswith("ollama/") else LLM_MODEL

logger.info(f"初始化 Ollama 模型: {model_name} @ {OLLAMA_BASE_URL}")

# 使用 LangChain 1.0 推荐的 ChatOllama
llm = ChatOllama(
    model=model_name,
    base_url=OLLAMA_BASE_URL,
    temperature=0.0,
)

logger.info("LLM 初始化成功")
