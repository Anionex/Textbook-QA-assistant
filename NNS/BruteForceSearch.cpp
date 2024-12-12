#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
namespace py = pybind11;
using namespace std;
// 用于排序的结构体
struct DistanceIndex {
    double distance;
    int index;
};

// 快速选择算法
int partition(DistanceIndex arr[], int left, int right) {
    DistanceIndex pivot = arr[right];
    int i = left - 1;
    
    for (int j = left; j < right; j++) {
        if (arr[j].distance < pivot.distance || 
            (arr[j].distance == pivot.distance && arr[j].index < pivot.index)) {
            i++;
            DistanceIndex temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }
    DistanceIndex temp = arr[i + 1];
    arr[i + 1] = arr[right];
    arr[right] = temp;
    return i + 1;
}

void quickselect(DistanceIndex arr[], int left, int right, int k) {
    if (left < right) {
        int pivot_index = partition(arr, left, right);
        if (pivot_index == k)
            return;
        else if (k < pivot_index)
            quickselect(arr, left, pivot_index - 1, k);
        else
            quickselect(arr, pivot_index + 1, right, k);
    }
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
    float* vectors_ptr,
    float* query_ptr,
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
        
        for(int j = 0; j < dim; j++) {
            double v1 = static_cast<double>(vectors_ptr[i * dim + j]);
            double v2 = static_cast<double>(query_ptr[j]);
            dot_product += v1 * v2;
            norm1 += v1 * v1;
            norm2 += v2 * v2;
        }
        
        double similarity = dot_product / (sqrt(norm1) * sqrt(norm2));
        distances[i] = {-similarity, i};
    }
    
    // 使用快速选择算法找到前k个元素
    quickselect(distances, 0, n_vectors - 1, top_k - 1);
    
    // 对前k个元素使用冒泡排序
    bubble_sort(distances, top_k);
    
    int* result = new int[top_k];
    for(int i = 0; i < top_k; i++) result[i] = distances[i].index;
    
    delete[] distances;
    return result;
}

py::array_t<int> brute_force_search(
    py::array_t<float> vectors,
    py::array_t<float> query,
    int top_k
) {
    if (top_k <= 0) throw runtime_error("invalid top_k value");
    
    // 数据验证和转换
    // array_t 就像是一个包裹
    // buffer_info 是包裹上的标签，告诉我们里面是什么
    // ptr 是实际打开包裹后能拿到的东西
    auto vectors_buf = vectors.request(); 
    auto query_buf = query.request();
    if (vectors_buf.ndim != 2) throw runtime_error("vectors must be 2-dimensional");
    if (query_buf.ndim != 1) throw runtime_error("query must be 1-dimensional");
    
    float* vectors_ptr = static_cast<float*>(vectors_buf.ptr);
    float* query_ptr = static_cast<float*>(query_buf.ptr);
    int n_vectors = vectors_buf.shape[0];
    int dim = vectors_buf.shape[1];
    
    if (query_buf.shape[0] != dim) throw runtime_error("query dimension must match vectors dimension");

    // 调用核心搜索逻辑
    int* result = brute_force_search_core(vectors_ptr, query_ptr, n_vectors, dim, top_k);
    
    auto result_array = py::array_t<int>(top_k, result);
    
    delete[] result;
    
    return result_array;
}