from react_agent import ReactAgent
from tool_registry import ToolRegistry, Tools
from tool_funcs import RAG_search, calculator, google_search
                


if __name__ == "__main__":
    agent = ReactAgent(model="qwen-max")
    agent.tools.add_tool(
        name_for_human="Economics RAG search",
        name_for_model="economics_rag_search",
        func=RAG_search,
        description="Economics RAG search是一个基于向量数据库的搜索工具，可用于搜索经济学相关著作的内容。此工具基于语义搜索，请你使用该工具时构造适合语义相似度搜索的搜索关键词句。",
        parameters=[
            {
                'name': 'query',
                'description': '搜索关键词或短语',
                'required': True,
                'schema': {'type': 'string'},
            }
        ]
    )
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
    
    
    agent.run("经济学中反常识的结论有哪些？", extra_requirements="")