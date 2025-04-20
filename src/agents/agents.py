
from langgraph.prebuilt import create_react_agent
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template
from src.tools import tavily_tool, python_repl_tool

def create_agent(agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with consistent configuration."""
    return create_react_agent(
        get_llm_by_type(AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=lambda state: apply_prompt_template(prompt_template, state),
    )


# Create agents using the factory function
research_agent = create_agent("researcher", [tavily_tool], "researcher")
coder_agent = create_agent("coder", [python_repl_tool], "coder")
reporter_agent = create_agent("reporter", [], "reporter")