#include <cmath>
#include <iostream>
#include <ctime>
using namespace std;

clock_t start_time, end_time;

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

int main() {
    freopen("input.txt", "r", stdin);
    // freopen("output.txt", "w", stdout);

    int n, d, k, nq;
    cin >> n >> d >> k;
    float* vectors = new float[n * d];
    for(int i = 0; i < n; i++) {
        for(int j = 0; j < d; j++) {
            cin >> vectors[i * d + j];
        }
    }
    start_time = clock();
    cin >> nq;
    float* query = new float[d];
    for(int i = 0; i < nq; i++) {
        // cout << "query " << i << ": ";
        for(int j = 0; j < d; j++) {
            cin >> query[j];
        }
        int* result = brute_force_search_core(vectors, query, n, d, k);
        for(int j = 0; j < k; j++) {
            // cout << result[j] << " ";
        }
        // cout << endl;
    }
    end_time = clock();
    cout << "frequency: " << (double)nq / ((end_time - start_time) / CLOCKS_PER_SEC) << endl;
    // cout << "Time taken: " << (end_time - start_time) / CLOCKS_PER_SEC << " seconds" << endl;
    return 0;
}
