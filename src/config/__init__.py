"""配置常量constant和团队成员定义"""

# 团队成员配置
TEAM_MEMBER_CONFIGRATIONS = {
    "researcher": {
        "name": "researcher",
        # "desc_for_llm": "Uses search to gather information from the internet. Outputs a summary of findings."
        "desc_for_llm": "Performs iterative, in-depth web search using ReAct (tavily_tool). Gathers, refines, and synthesizes information, providing structured findings."
    },
    "coder": {
        "name": "coder",
        # "desc_for_llm": "Executes Python code and performs calculations. Can solve math problems and analyze data."
        "desc_for_llm": "Executes Python/bash code. Performs data analysis (pandas, numpy) & visualization (matplotlib, seaborn). Handles calculations. Needs clear instructions & data. **Does NOT perform qualitative analysis or research.**"
    },
    "reporter": {
        "name": "reporter",
        "desc_for_llm": "Writes professional reports based on gathered information, with proper formatting and citations."
    }
}

# 团队成员列表
TEAM_MEMBERS = list(TEAM_MEMBER_CONFIGRATIONS.keys())

# 默认API配置
# deepseek
# REASONING_MODEL = "deepseek-chat"
# BASIC_MODEL = "deepseek-chat"

# openai
REASONING_MODEL = "gpt-4.1-2025-04-14"
BASIC_MODEL = "gpt-4.1-2025-04-14"
# BASIC_MODEL = "gpt-4.1-mini-2025-04-14"

# qwen
# REASONING_MODEL = "qwen-max"
# BASIC_MODEL = "qwen-max"

# # 中转站
# REASONING_MODEL = "o3-mini"
# BASIC_MODEL = "o3-mini"

# 搜索配置
SEARCH_MAX_RESULTS = 5
TAVILY_MAX_RESULTS = 5
