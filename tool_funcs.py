import os
import json
import requests
import dotenv
from vec_db import VectorDB

dotenv.load_dotenv()



# 添加计算器工具
def calculator(expression: str):
    return eval(expression)



# 添加谷歌搜索工具
def google_search(search_query: str):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": search_query})
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response['organic'][0]['snippet']

# 模拟进行向量数据库构建

# 初始化向量数据库
vec_db = VectorDB()
# 加载文档
vec_db.add_documents("docs/曼昆 经济学原理.txt", force_reprocess=False)
vec_db.add_documents("docs/亚当·斯密 国富论.txt", force_reprocess=False)
    
def RAG_search(query: str) -> str:
    """
    使用RAG技术进行搜索文档库内容，返回搜索结果。
    流程：
    1. 初始化向量数据库
    2. 搜索查找最相似的文档片段
    3. 返回搜索结果
    """


    # 使用暴力搜索查找相似内容
    results = vec_db.search_with_brute_force(query, top_k=3)
    
    # 如果没有找到结果，返回提示信息
    if not results:
        return "未找到相关内容。"
    
    # 组合搜索结果
    response = "找到以下相关内容：\n\n"
    for idx, result in enumerate(results, 1):
        
        response += f"{idx}. 来自文件: {os.path.basename(result['file_path'])}\n"
        response += f"内容: {result['chunk_text']}\n\n"
        response += "*"*100 + "\n"
    
    return response


if __name__ == "__main__":
    query = "什么是宏观经济学"
    result = RAG_search(query)
    print(result)




