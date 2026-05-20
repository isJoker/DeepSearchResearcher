from agent.load_prompts import sub_agents_config
from tools.ragflow_tools import get_assistant_list , create_ask_delete

# 核心依赖（SDK+环境变量+请求库）
# pip install ragflow_sdk python-dotenv requests
# # LangChain 集成依赖（适配 Agent 工具调用）
# pip install langchain-core typing-extensions

knowledge_base_agent = {
    "name":sub_agents_config['ragflow']['name'],
    "description":sub_agents_config['ragflow']['description'],
    "system_prompt":sub_agents_config['ragflow']['system_prompt'],
    "tools":[get_assistant_list,create_ask_delete]
}