import logging
import os
from langchain.tools import Tool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from src.config import TAVILY_MAX_RESULTS
from .decorators import log_io

logger = logging.getLogger(__name__)

# 检查API密钥
if "TAVILY_API_KEY" not in os.environ:
    logger.warning("TAVILY_API_KEY not set in environment.")

# 创建搜索API封装器
search_wrapper = TavilySearchAPIWrapper()

@log_io
def tavily_search(query: str) -> str:
    """Search the internet for information on a specific query."""
    try:
        logger.info(f"HTTP Request: Tavily search for query: {query[:50]}...")  # 类似DeepSeek的日志
        # 使用results方法获取搜索结果
        results = search_wrapper.results(query=query, max_results=TAVILY_MAX_RESULTS)
        if isinstance(results, list):
            logger.info(f"HTTP Response: Tavily returned {len(results)} results")  # 类似DeepSeek的日志
            return results
        else:
            logger.warning(f"HTTP Response: Tavily returned unexpected format: {type(results)}")
            return str(results)
    except Exception as e:
        logger.error(f"Error in Tavily search: {e}")
        return f"Search error: {str(e)}"

# 创建标准化工具对象
tavily_tool = Tool(
    name="tavily_search",
    description="Search the internet for information on a specific query or topic.",
    func=tavily_search,
)