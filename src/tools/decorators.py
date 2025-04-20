import logging
import functools
from typing import Any, Callable, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def log_io(func: Callable) -> Callable:
    """
    A decorator that logs the input parameters and output of a tool function.
    记录工具函数的输入参数和返回结果，方便调试和跟踪

    Args:
        func: The tool function to be decorated

    Returns:
        The wrapped function with input/output logging
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Log input parameters
        func_name = func.__name__
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {func_name} called with parameters: {params}")

        # Execute the function
        result = func(*args, **kwargs)

        # Log the output
        logger.debug(f"Tool {func_name} returned: {result}")

        return result

    return wrapper


class LoggedToolMixin:
    """
    A mixin class that adds logging functionality to any tool.
    LangChain的工具类通常有一个_run方法，是工具实际执行逻辑的地方。
    这个混入类通过方法覆盖，在不修改原始类代码的情况下增加了日志功能。
    """

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """Helper method to log tool operations."""
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Override _run method to add logging."""
        self._log_operation("_run", *args, **kwargs)
        result = super()._run(*args, **kwargs)
        logger.debug(
            f"Tool {self.__class__.__name__.replace('Logged', '')} returned: {result}"
        )
        return result


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    Factory function to create a logged version of any tool class.
    类工厂函数，动态创建增强版工具类：
    1. 创建一个新类，同时继承LoggedToolMixin和原始工具类
    2. 设置新类名
    3. 返回新类（注意返回的是类定义，不是实例）

    Args:
        base_tool_class: The original tool class to be enhanced with logging

    Returns:
        A new class that inherits from both LoggedToolMixin and the base tool class
    """

    # 创建一个具名的子类而不是匿名内部类
    tool_name = f"Logged{base_tool_class.__name__}"
    
    # 动态创建新类，确保类名明确
    LoggedTool = type(
        tool_name,
        (LoggedToolMixin, base_tool_class),
        {
            "__module__": "src.tools.decorators",
            "__qualname__": tool_name,
        }
    )
    
    # 复制原工具类的重要属性
    if hasattr(base_tool_class, "name"):
        LoggedTool.name = getattr(base_tool_class, "name")
    if hasattr(base_tool_class, "description"):
        LoggedTool.description = getattr(base_tool_class, "description")
    
    return LoggedTool