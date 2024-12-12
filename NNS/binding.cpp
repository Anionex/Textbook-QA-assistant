#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
py::array_t<int> brute_force_search(py::array_t<float>, py::array_t<float>, int);
py::array_t<int> hash_search(py::array_t<float>, py::array_t<float>, int);
py::array_t<int> hnsw_search(py::array_t<float>, py::array_t<float>, int);

namespace py = pybind11;

PYBIND11_MODULE(nns_search, m) {
    m.doc() = "近邻搜索算法的C++实现，包含暴力搜索、哈希搜索和HNSW搜索";
    m.def("brute_force_search", &brute_force_search);
    m.def("hash_search", &hash_search);
    m.def("hnsw_search", &hnsw_search);
}