"""
日志配置模块
配置应用程序的日志系统
"""
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file=None):
    """
    设置应用程序日志
    
    Args:
        log_level: 日志级别（默认 INFO）
        log_file: 日志文件路径（可选）
    """
    # 创建根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除现有handlers
    root_logger.handlers.clear()
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件handler（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 设置第三方库日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    logging.info("日志系统初始化完成")

# 默认初始化（可通过环境变量控制）
import os
log_level_str = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_str.upper(), logging.INFO)
log_file = os.getenv("LOG_FILE")

setup_logging(log_level=log_level, log_file=log_file)
