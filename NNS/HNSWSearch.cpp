#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
namespace py = pybind11;

// 用于存储距离和索引的辅助结构体
struct DistanceIndex {
    double distance;
    int index;
};

int partition(DistanceIndex arr[], int left, int right) ;
void quickselect(DistanceIndex arr[], int left, int right, int k);
void bubble_sort(DistanceIndex arr[], int k);

py::array_t<int> hnsw_search(
    py::array_t<float> vectors,
    py::array_t<float> query,
    int top_k
) {
    // 获取数组信息
    auto vectors_buf = vectors.request();
    auto query_buf = query.request();
    
    if (vectors_buf.ndim != 2) {
        throw std::runtime_error("vectors must be 2-dimensional");
    }
    if (query_buf.ndim != 1) {
        throw std::runtime_error("query must be 1-dimensional");
    }
    
    float* vectors_ptr = static_cast<float*>(vectors_buf.ptr);
    float* query_ptr = static_cast<float*>(query_buf.ptr);
    
    int n_vectors = vectors_buf.shape[0];
    int dim = vectors_buf.shape[1];
    
    if (query_buf.shape[0] != dim) {
        throw std::runtime_error("query dimension must match vectors dimension");
    }

    if (top_k <= 0) {
        throw std::runtime_error("invalid top_k value");
    }
    top_k = std::min(top_k, n_vectors);
    
    // 使用C风格数组分配
    DistanceIndex* distances = new DistanceIndex[n_vectors];
    
    // 计算距离
    for(int i = 0; i < n_vectors; i++) {
        double dot_product = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for(int j = 0; j < dim; j++) {
            double v1 = static_cast<double>(vectors_ptr[i * dim + j]);
            double v2 = static_cast<double>(query_ptr[j]);
            dot_product += v1 * v2;
            norm1 += v1 * v1;
            norm2 += v2 * v2;
        }
        
        double similarity = dot_product / (std::sqrt(norm1) * std::sqrt(norm2));
        distances[i] = {-similarity, i};
    }
    
    // 使用快速选择算法找到前k个元素
    quickselect(distances, 0, n_vectors - 1, top_k - 1);
    
    // 对前k个元素使用冒泡排序
    bubble_sort(distances, top_k);
    
    // 准备结果数组
    int* result = new int[top_k];
    for(int i = 0; i < top_k; i++) {
        result[i] = distances[i].index;
    }
    
    // 将结果转换为 py::array_t<int>
    auto result_array = py::array_t<int>(top_k, result);
    
    // 清理内存
    delete[] result;
    delete[] distances;
    
    return result_array;
}