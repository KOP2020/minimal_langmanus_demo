from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from src.config import TEAM_MEMBERS
from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    supervisor_node,
    research_node,
    code_node,
    reporter_node,
)


def build_graph():
    """Build the agent workflow graph."""
    # Use memory saver for persistance
    memory = MemorySaver()
    
    # Create state graph
    builder = StateGraph(State)
    
    # Add starting node
    builder.add_edge(START, "coordinator")
    
    # Add nodes to graph
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("planner", planner_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)
    builder.add_node("reporter", reporter_node)
    
    # Return compiled graph
    return builder.compile(checkpointer=memory)