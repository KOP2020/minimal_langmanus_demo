import os
import sys
import logging
from typing import Dict, Any

# 设置API密钥
# deepseek
# os.environ["OPENAI_API_KEY"] = "sk-c0d8d7df5e1744eb86e27e0470edfdfb"  
 

# openai
os.environ["OPENAI_API_KEY"] = "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"

# 中转站
# os.environ["OPENAI_API_KEY"] = "sk-IrPR9ISbUJNd4QCg30A9CeA0Bf81464cB78cA9C1F4AbCa8f"


# qwen
# os.environ["OPENAI_API_KEY"] = "sk-d369918cdca342828177292ff6d4308c"

# tavily api-key
os.environ["TAVILY_API_KEY"] = "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"

from src.workflow import run_agent_workflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_messages(result: Dict[str, Any]) -> None:
    """
    Print the message history in a readable format.
    
    Args:
        result: Workflow result containing messages
    """
    print("\n" + "=" * 40 + " CONVERSATION " + "=" * 40)
    
    for msg in result["messages"]:
        # Handle different message formats
        if isinstance(msg, dict):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            name = msg.get("name", "")
        else:
            # For BaseMessage objects
            role = getattr(msg, "type", "unknown")
            content = getattr(msg, "content", "")
            name = getattr(msg, "name", "")
        
        # Format message header
        header = f"[{role.upper()}"
        if name:
            header += f" - {name}"
        header += "]"
        
        # Print formatted message
        print("\n" + "-" * 80)
        print(f"{header}")
        print("-" * 80)
        print(f"{content}")
    
    print("\n" + "=" * 90)


def main() -> None:
    """Main entry point for the application."""
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        api_key = input("Please enter your OpenAI API key: ").strip()
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Get user query from command line or prompt
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your question: ").strip()
    
    if not user_query:
        print("No query provided. Exiting.")
        return
    
    # Run the workflow
    try:
        result = run_agent_workflow(user_input=user_query)
        print_messages(result)
    except Exception as e:
        logger.error(f"Error running workflow: {e}", exc_info=True)
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()