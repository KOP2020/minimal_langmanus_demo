"""LLM接口实现，提供不同类型的语言模型"""
import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI

from src.config.agents import LLMType
from src.config import REASONING_MODEL, BASIC_MODEL

# LLM实例缓存
_llm_cache: Dict[str, Any] = {}

def get_llm_by_type(llm_type: LLMType):
    """
    获取指定类型的LLM实例
    
    Args:
        llm_type: LLM类型，可选 "basic" 或 "reasoning"
        
    Returns:
        配置好的LLM实例
    """
    # 检查缓存
    if llm_type in _llm_cache:
        return _llm_cache[llm_type]
    
    # # 使用DeepSeek API (与OpenAI兼容)
    # base_url = "https://api.deepseek.com/v1"  # DeepSeek API端点

    # 使用OpenAI API
    base_url = "https://api.openai.com/v1"  # OpenAI API端点

    # 中转站
    # base_url = "https://api.gptapi.us/v1/chat/completions"

    # 使用Qwen API
    # base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    if llm_type == "reasoning":
        # 使用更强大的模型进行复杂推理
        llm = ChatOpenAI(
            model=REASONING_MODEL,  # DeepSeek的模型
            temperature=0.0,
            base_url=base_url,
            api_key=os.environ["OPENAI_API_KEY"],  # 使用设置的API密钥
            # streaming=True  # 启用流式模式
        )
    else:  # basic
        # 使用更快的模型进行简单决策
        llm = ChatOpenAI(
            model=BASIC_MODEL,  # DeepSeek的模型
            temperature=0.0,
            base_url=base_url,
            api_key=os.environ["OPENAI_API_KEY"],
            # streaming=True  # 启用流式模式
        )
    
    # 缓存实例
    _llm_cache[llm_type] = llm
    return llm