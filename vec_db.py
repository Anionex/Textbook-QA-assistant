from utils import file_processor, text_processor
import numpy as np
import dashscope
from http import HTTPStatus
from sklearn.neighbors import NearestNeighbors
from nns_search import hash_search, brute_force_search, hnsw_search
DEBUG = True

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
        self.document_vectors: list[VectorDB.DocumentVector] = []  # 存储文档向量及元数据
        self.embedder = TextEmbedder()

    def get_embeddings(self, chunks: list[str]) -> list[np.ndarray]:
        return self.embedder.embed_with_str(chunks)
    
    def add_documents(self, file_path: str):
        # 提取文本
        text = file_processor.extract_text(file_path)
        # 分割文本
        if DEBUG:
            chunks = text_processor.split_text_by_sentence(text)[:2]
        else:
            chunks = text_processor.split_text_by_sentence(text)
        # embedding化
        embeddings = self.get_embeddings(chunks)
        
        # 存储文档向量及元数据
        for chunk_text, embedding in zip(chunks, embeddings):
            doc_vector = self.DocumentVector(file_path, chunk_text, embedding)
            self.document_vectors.append(doc_vector)
    
    def delete_documents(self, file_path: str):
        pass
    
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
    
    def search_with_hash(self, query: str, top_k: int = 10):
        query_vector = np.array(self.get_embeddings([query])[0], dtype=np.float32)
        db_vectors = np.array([doc.vector for doc in self.document_vectors], dtype=np.float32)
        
        indices = hash_search(db_vectors, query_vector, top_k)
        
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
        
        indices = hnsw_search(db_vectors, query_vector, top_k)
        
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
        pass
    
if __name__ == "__main__":
    db = VectorDB()
    DEBUG = False
    # db.add_documents("docs/2405.16506v2-GRAG.pdf")
    # result = db.search("introduction of GRAG")
    
    db.add_documents("docs/三体.txt")
    query = "杨冬自杀的原因"
    result = db.search_with_brute_force(query)
    print(f"\n=== Search Results for '{query} using brute force' ===\n")
    
    for i, item in enumerate(result, 1):
        print(f"Result #{i}:")
        print(f"File: {item['file_path']}")
        print(f"Text: {item['chunk_text']}")
        print(f"Index: {item['index']}")
        print("-" * 80 + "\n")
        
    # 使用sklearn
    result = db.search_with_sklearn(query)
    print(f"\n=== Search Results for '{query} using sklearn' ===\n")
    for i, item in enumerate(result, 1):
        print(f"Result #{i}:")
        print(f"File: {item['file_path']}")
        print(f"Text: {item['chunk_text']}")
        print(f"Index: {item['index']}")
        print("-" * 80 + "\n")

    # embedder = TextEmbedder()
    # print(embedder.embed_with_str(["What is GRAG?", "What is GRAG?", "who are you?"]))

