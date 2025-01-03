#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <iostream>
namespace py = pybind11;
using namespace std;

#define SEARCH_TIMES 4000

// 用于排序的数据结构
struct DistanceIndex {
    double distance;
    int index;
};

void quickselect(DistanceIndex arr[], int l, int r, int k) {
    if (l >= r) return;
    int i = l, j = r;
    DistanceIndex mid = arr[(l + r) / 2];
    
    while (i <= j) {
        while (arr[i].distance < mid.distance) ++i;
        while (arr[j].distance > mid.distance) --j;
        if (i <= j) {
            DistanceIndex temp = arr[i];
            arr[i] = arr[j]; 
            arr[j] = temp;
            ++i, --j;
        }
    }
    
    if (k > i) quickselect(arr, i, r, k); else
    if (j>= k) quickselect(arr, l, j, k);
}

void bubble_sort(DistanceIndex arr[], int k) {
    for (int i = 0; i < k - 1; i++) {
        for (int j = 0; j < k - i - 1; j++) {
            if (arr[j].distance > arr[j + 1].distance || 
                (arr[j].distance == arr[j + 1].distance && arr[j].index > arr[j + 1].index)) {
                DistanceIndex temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int* brute_force_search_core(
    float* vectors,
    float* query,
    int n_vectors,
    int dim,
    int top_k
) {
    top_k = min(top_k, n_vectors);
    
    DistanceIndex* distances = new DistanceIndex[n_vectors];
    
    // 计算距离
    for(int i = 0; i < n_vectors; i++) {
        double dot_product = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;

        // 余弦相似度计算公式：cos(θ) = (A·B)/(|A|·|B|)
        for(int j = 0; j < dim; j++) {
            double v1 = static_cast<double>(vectors[i * dim + j]);
            double v2 = static_cast<double>(query[j]);
            dot_product += v1 * v2;
            norm1 += v1 * v1;
            norm2 += v2 * v2;
        }
        
        double similarity = dot_product / (sqrt(norm1) * sqrt(norm2));
        distances[i] = {-similarity, i};
    }
    
    quickselect(distances, 0, n_vectors - 1, top_k - 1);
    bubble_sort(distances, top_k);
    
    int* result = new int[top_k];
    for(int i = 0; i < top_k; i++) {
        result[i] = distances[i].index;
    }
    
    delete[] distances;
    return result;
}

py::array_t<int> brute_force_search(
    py::array_t<float> vectors,
    py::array_t<float> query,
    int top_k
) {
    if (top_k <= 0) {
        throw std::runtime_error("invalid top_k value");
    }
    
    auto vectors_buf = vectors.request();
    auto query_buf = query.request();
    
    if (vectors_buf.ndim != 2) throw std::runtime_error("vectors must be 2-dimensional");
    if (query_buf.ndim != 1) throw std::runtime_error("query must be 1-dimensional");
    
    // Get raw pointers from numpy arrays
    float* vectors_ptr = static_cast<float*>(vectors_buf.ptr);
    float* query_ptr = static_cast<float*>(query_buf.ptr);
    
    int n_vectors = static_cast<int>(vectors_buf.shape[0]);
    int dim = static_cast<int>(vectors_buf.shape[1]);
    
    if (query_buf.shape[0] != static_cast<size_t>(dim)) 
        throw std::runtime_error("query dimension must match vectors dimension");

    // int* result = brute_force_search_core(vectors_ptr, query_ptr, n_vectors, dim, top_k);
    // 单纯暴力搜索
    int* result = new int[top_k];
    for(int i = 0; i < SEARCH_TIMES; i++) {
        result = brute_force_search_core(vectors_ptr, query_ptr, n_vectors, dim, top_k);
    }
    // Create numpy array from result
    py::array_t<int> result_array(top_k);
    auto result_buf = result_array.request();
    int* result_ptr = static_cast<int*>(result_buf.ptr);
    std::memcpy(result_ptr, result, top_k * sizeof(int));
    
    delete[] result;
    return result_array;
}