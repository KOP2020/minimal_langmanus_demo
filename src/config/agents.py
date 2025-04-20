"""Agent和LLM类型映射配置"""
from typing import Literal

# LLM类型
LLMType = Literal["basic", "reasoning"]

# LLM类型映射
AGENT_LLM_MAP: dict[str, LLMType]  = {
    "coordinator": "basic",
    "planner": "reasoning",
    "supervisor": "basic",
    "researcher": "basic",
    "coder": "basic",
    "reporter": "reasoning"
}

# 搜索结果最大数量
SEARCH_MAX_RESULTS = 5