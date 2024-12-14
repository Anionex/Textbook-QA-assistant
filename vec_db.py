import time
from utils import file_processor, text_processor
import numpy as np
import dashscope
from http import HTTPStatus
from sklearn.neighbors import NearestNeighbors
from nns_search import brute_force_search, hnsw_search
import os
import pickle
import hashlib

DEBUG = True

# 添加新的常量定义
VECTOR_CACHE_DIR = "vector_cache"

class TextEmbedder:
    def __init__(self, model=dashscope.TextEmbedding.Models.text_embedding_v1):
        self.model = model

    def embed_with_str(self, text: list[str]) -> list[np.ndarray] | None:
        print("start to embed text:", text)
        embeddings = []
        
        #  batch 25
        for i in range(0, len(text), 25):
            batch = text[i:i+25]
            resp = dashscope.TextEmbedding.call(
                model=self.model,
                input=batch)
                
            if resp.status_code == HTTPStatus.OK:
                batch_embeddings = []
                for item in resp.output['embeddings']:
                    batch_embeddings.append(np.array(item['embedding']))
                embeddings.extend(batch_embeddings)
            else:
                print("embed text failed:", resp)
                return None
                
        return embeddings

class VectorDB:
    class DocumentVector:
        def __init__(self, file_path: str, chunk_text: str, vector: np.ndarray):
            self.file_path = file_path
            self.chunk_text = chunk_text
            self.vector = vector

    def __init__(self):
        self.document_vectors: list[VectorDB.DocumentVector] = []
        self.embedder = TextEmbedder()
        # 确保缓存目录存在
        os.makedirs(VECTOR_CACHE_DIR, exist_ok=True)

    def _get_cache_path(self, file_path: str) -> str:
        # 使用文件路径的哈希作为缓存文件名，避免文件名过长或包含特殊字符
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return os.path.join(VECTOR_CACHE_DIR, f"{file_hash}.pkl")

    def _save_to_cache(self, file_path: str, chunks: list[str], embeddings: list[np.ndarray]):
        cache_data = {
            'chunks': chunks,
            'embeddings': embeddings,
            'file_path': file_path
        }
        cache_path = self._get_cache_path(file_path)
        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)

    def _load_from_cache(self, file_path: str) -> tuple[list[str], list[np.ndarray]] | None:
        cache_path = self._get_cache_path(file_path)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                # 验证缓存数据是否匹配当前文件
                if cache_data['file_path'] == file_path:
                    return cache_data['chunks'], cache_data['embeddings']
            except Exception as e:
                print(f"Error loading cache: {e}")
        return None

    def get_embeddings(self, chunks: list[str]) -> list[np.ndarray]:
        return self.embedder.embed_with_str(chunks)
    
    def add_documents(self, file_path: str, force_reprocess: bool = False):
        # 检查缓存
        cache_result = self._load_from_cache(file_path)
        
        if cache_result is not None and not force_reprocess:
            print(f"Loading vectors from cache for {file_path}")
            chunks, embeddings = cache_result
        else:
            print(f"Processing new document: {file_path}")
            # 提取文本
            text = file_processor.extract_text(file_path)
            # 分割文本
            if DEBUG:
                chunks = text_processor.split_text_by_sentence(text)[:2]
            else:
                chunks = text_processor.split_text_by_sentence(text)
            # embedding化
            embeddings = self.get_embeddings(chunks)
            # 保存到缓存
            self._save_to_cache(file_path, chunks, embeddings)
        
        # 存储文档向量及元数据
        for chunk_text, embedding in zip(chunks, embeddings):
            doc_vector = self.DocumentVector(file_path, chunk_text, embedding)
            self.document_vectors.append(doc_vector)
    
    def delete_documents(self, file_path: str):
        # 删除文档向量
        self.document_vectors = [dv for dv in self.document_vectors if dv.file_path != file_path]
        # 删除缓存
        cache_path = self._get_cache_path(file_path)
        if os.path.exists(cache_path):
            os.remove(cache_path)
    
    def search_with_sklearn(self, query: str, top_k: int = 10):
        query_vector = np.array(self.get_embeddings([query])[0], dtype=np.float32)
        # 构建向量矩阵
        db_vectors = np.array([doc.vector for doc in self.document_vectors], dtype=np.float32)
        
        # 使用sklearn的NearestNeighbors替换cpp_search
        nn = NearestNeighbors(n_neighbors=min(top_k, len(db_vectors)), metric='cosine')
        nn.fit(db_vectors)
        distances, indices = nn.kneighbors([query_vector])
        
        
        # 返回搜索结果，包含文档路径和文本片段
        results = []
        for idx in indices[0]:  # indices是2D数组，我们只需要第一行
            doc_vector = self.document_vectors[idx]
            results.append({
                'file_path': doc_vector.file_path,
                'chunk_text': doc_vector.chunk_text,
                'index': idx
            })
        return results
    
    def search_with_brute_force(self, query: str, top_k: int = 10):
        # Get query embedding and convert to numpy array
        query_vector = np.array(self.get_embeddings([query])[0], dtype=np.float32)
        # Get database vectors
        db_vectors = np.array([doc.vector for doc in self.document_vectors], dtype=np.float32)
        
        # Call C++ brute force search
        indices = brute_force_search(db_vectors, query_vector, top_k)
        
        # Format results
        results = []
        for idx in indices:
            doc_vector = self.document_vectors[idx]
            results.append({
                'file_path': doc_vector.file_path,
                'chunk_text': doc_vector.chunk_text,
                'index': idx
            })
        return results
     
    def search_with_hnsw(self, query: str, top_k: int = 10):
        query_vector = np.array(self.get_embeddings([query])[0], dtype=np.float32)
        db_vectors = np.array([doc.vector for doc in self.document_vectors], dtype=np.float32)
        try:
            print(f"db_vectors shape: {db_vectors.shape}, query_vector shape: {query_vector.shape}")
            indices = hnsw_search(db_vectors, query_vector, top_k)
        except RuntimeError as e:
            print(f"Error occurred: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []
        
        results = []
        for idx in indices:
            doc_vector = self.document_vectors[idx]
            results.append({
                'file_path': doc_vector.file_path,
                'chunk_text': doc_vector.chunk_text,
                'index': idx
            })
        return results
    
    def update_documents(self, file_path: str):
        self.delete_documents(file_path)
        self.add_documents(file_path, force_reprocess=True)

def show_vector_info(db: VectorDB): 
    total_text_length = 0
    # 显示db中所有的vectors的元数据
    print("-" * 80)
    print("All vectors info:")
    for index, vector in enumerate(db.document_vectors, 1):
        total_text_length += len(vector.chunk_text)
        # print(f"Vector Index: {index}, chunk size: {len(vector.chunk_text)}")
    print("-" * 80)
    print(f"Total text length: {total_text_length}")
    print(f"Total vectors: {len(db.document_vectors)}")
    print(f"Average chunk size: {total_text_length / len(db.document_vectors)}")
    # print(f"Last's chunk content: {db.document_vectors[-1].chunk_text}")
    

if __name__ == "__main__":
    db = VectorDB()
    DEBUG = False
    # db.add_documents("docs/2405.16506v2-GRAG.pdf")
    # result = db.search("introduction of GRAG")
    
    db.add_documents("docs/曼昆 经济学原理.txt", force_reprocess=False)
    db.add_documents("docs/亚当·斯密 国富论.txt", force_reprocess=False)
    query = "什么是宏观经济学"
    
    show_vector_info(db)
    
    # exit()
    # 使用暴力搜索
    start_time = time.time()
    num = 5
    result = db.search_with_brute_force(query, num)
    end_time = time.time()
    time_brute_force = end_time - start_time
    print(f"\n=== Search Results for '{query} using brute force' ===")
    print(f"Search time: {time_brute_force:.4f} seconds\n")
    
    for i, item in enumerate(result, 1):
        # print(f"Result #{i}:")
        # print(f"File: {item['file_path']}")
        # print(f"Text: {item['chunk_text']}")
        print(f"Index: {item['index']}")
        # print("-" * 80 + "\n")
        
    # 使用sklearn
    start_time = time.time()
    result = db.search_with_sklearn(query, num)
    end_time = time.time()
    time_sklearn = end_time - start_time
    print(f"\n=== Search Results for '{query} using sklearn' ===")
    print(f"Search time: {time_sklearn:.4f} seconds\n")
    
    for i, item in enumerate(result, 1):
        # print(f"Result #{i}:")
        # print(f"File: {item['file_path']}")
        # print(f"Text: {item['chunk_text']}")
        print(f"Index: {item['index']}")
        # print("-" * 80 + "\n")

    # 使用hnsw
    start_time = time.time()
    result = db.search_with_hnsw(query, num)
    end_time = time.time()
    time_hnsw = end_time - start_time
    print(f"\n=== Search Results for '{query} using hnsw' ===")
    print(f"Search time: {time_hnsw:.4f} seconds\n")

    for i, item in enumerate(result, 1):
        # print(f"Result #{i}:")
        # print(f"File: {item['file_path']}")
        # print(f"Text: {item['chunk_text']}")
        print(f"Index: {item['index']}")
        # print("-" * 80 + "\n")

    print(f"Brute force search time: {time_brute_force:.4f} seconds")
    print(f"Sklearn search time: {time_sklearn:.4f} seconds")
    print(f"Hnsw search time: {time_hnsw:.4f} seconds")
    # embedder = TextEmbedder()
    # print(embedder.embed_with_str(["What is GRAG?", "What is GRAG?", "who are you?"]))


