# 目标： 创建网络搜索子智能体
# 方式1： dict -> deepagents  方式： compiledSubAgent -> langchain langgraph
from agent.load_prompts import sub_agents_config
from tools.tavily_tool import internet_search


network_search_agent = {
    "name":sub_agents_config['tavily']['name'],
    "description":sub_agents_config['tavily']['description'],
    "system_prompt":sub_agents_config['tavily']['system_prompt'],
    "tools":[internet_search]
}