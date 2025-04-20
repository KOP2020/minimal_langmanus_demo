import logging
from langchain_experimental.utilities import PythonREPL
from langchain.tools import Tool
from .decorators import create_logged_tool, log_io

logger = logging.getLogger(__name__)

# 创建基础PythonREPL实例
repl = PythonREPL()

# 使用函数式方法创建工具，这样可以确保工具有明确的名称
@log_io
def run_python_code(code: str) -> str:
    """Run Python code and return the result."""
    return repl.run(code)

# 创建标准化工具对象
python_repl_tool = Tool(
    name="python_repl",
    description="A Python REPL. Use this to execute python commands. Input should be a valid python command.",
    func=run_python_code,
)

