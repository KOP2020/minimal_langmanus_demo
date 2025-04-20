import logging
from typing import Dict, Any

from src.config import TEAM_MEMBERS, TEAM_MEMBER_CONFIGRATIONS
from src.graph import build_graph

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 
# Build the graph once
graph = build_graph()


def run_agent_workflow(user_input: str, debug: bool = False) -> Dict[str, Any]:
    """
    Run the agent workflow with the given user input.
    
    Args:
        user_input: User's query or request
        debug: Whether to enable debug mode
        
    Returns:
        Final state after workflow completion
    """
    if not user_input:
        raise ValueError("User input cannot be empty")
    
    logger.info(f"Starting workflow with user input: {user_input}")
    
    # Initialize state with user input and configuration
    initial_state = {
        # Constants
        "TEAM_MEMBERS": TEAM_MEMBERS,
        "TEAM_MEMBER_CONFIGRATIONS": TEAM_MEMBER_CONFIGRATIONS,
        # Runtime Variables
        "messages": [{"role": "user", "content": user_input}],
        "deep_thinking_mode": True,
        "search_before_planning": True,
    }
    
    # Set config for thread management
    config = {"configurable": {"thread_id": "default"}}
    
    # Run the graph
    result = graph.invoke(input=initial_state, config=config)
    
    logger.info("Workflow completed successfully")
    return result