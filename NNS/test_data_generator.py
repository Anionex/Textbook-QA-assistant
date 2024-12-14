import os
import numpy as np

def generate_test_data(n, d, k, nq, filename='input.txt'):
    # 生成n个d维的随机浮点数向量
    data_points = np.random.rand(n, d).astype(np.float32)
    
    # 生成nq个查询向量
    query_points = np.random.rand(nq, d).astype(np.float32)
    
    # 将数据写入文件
    with open(os.path.join(os.path.dirname(__file__), filename), 'w') as f:
        f.write(f"{n} {d} {k}\n")
        for point in data_points:
            f.write(" ".join(map(str, point)) + "\n")
        f.write(f"{nq}\n")
        for query in query_points:
            f.write(" ".join(map(str, query)) + "\n")
    full_path = os.path.join(os.path.dirname(__file__), filename)
    print(f"数据已成功写入文件: {full_path}")

# 参数设置
n = 1000  # 向量数量
d = 1536   # 向量维度
k = 10    # 最近邻数量
nq = 10  # 查询数量

generate_test_data(n, d, k, nq)
