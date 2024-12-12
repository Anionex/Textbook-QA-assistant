from react_agent import ReactAgent
from tool_registry import ToolRegistry, Tools
from tool_funcs import calculator, google_search
                


if __name__ == "__main__":
    agent = ReactAgent(model="qwen-max")
    
    agent.tools.add_tool(
        name_for_human="google search",
        name_for_model="google_search",
        func=google_search,
        description="google search是一个通用搜索引擎，可用于访问互联网、查询百科知识、了解时事新闻等。",
        parameters=[
            {
                'name': 'search_query',
                'description': '搜索关键词或短语',
                'required': True,
                'schema': {'type': 'string'},
            }
        ]
    )   
    
    
    agent.run("黑神话悟空至今盈利了多少？", extra_requirements="")