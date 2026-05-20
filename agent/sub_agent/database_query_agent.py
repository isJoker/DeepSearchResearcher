from agent.load_prompts import sub_agents_config
from tools.db_tool import list_sql_tables,get_table_data,execute_sql_query

database_query_agent = {
    "name":sub_agents_config['db']['name'],
    "description":sub_agents_config['db']['description'],
    "system_prompt":sub_agents_config['db']['system_prompt'],
    "tools":[list_sql_tables,get_table_data,execute_sql_query]
}