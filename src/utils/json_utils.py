import logging
import json
import re

logger = logging.getLogger(__name__)


def repair_json_output(content: str) -> str:
    """
    Repair and normalize JSON output.
    llm生成的response中，可能包含非JSON格式的内容，这个func用来取出纯净的JSON部分

    Args:
        content (str): String content that may contain JSON

    Returns:
        str: Repaired JSON string, or original content if not JSON
    """
    content = content.strip()
    
    # 如果是代码块格式的JSON，尝试提取JSON部分
    json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
    if json_block_match:
        try:
            json_content = json_block_match.group(1).strip()
            # 验证是否可解析
            json.loads(json_content)
            return json_content
        except json.JSONDecodeError:
            pass

    # 如果内容以花括号或方括号开头，可能是JSON
    if content.startswith(("{", "[")):
        try:
            # 尝试解析JSON
            json_obj = json.loads(content)
            return content
        except json.JSONDecodeError:
            # 尝试提取有效的JSON部分
            json_match = re.search(r'({[\s\S]*}|\[[\s\S]*\])', content)
            if json_match:
                try:
                    json_extract = json_match.group(1)
                    json.loads(json_extract)  # 验证
                    return json_extract
                except json.JSONDecodeError:
                    logger.warning("JSON修复失败")
    
    return content