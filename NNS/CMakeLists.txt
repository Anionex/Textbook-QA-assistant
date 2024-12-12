cmake_minimum_required(VERSION 3.10)
project(nns_search)

# 设置C++标准
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 查找Python 3.10
set(Python_ADDITIONAL_VERSIONS 3.10)
find_package(Python 3.10 EXACT COMPONENTS Interpreter Development REQUIRED)

# 查找pybind11
find_package(pybind11 REQUIRED)

# 添加源文件
set(SOURCES
    binding.cpp
    BruteForceSearch.cpp
    HashSearch.cpp
    HNSWSearch.cpp
)

# 创建Python模块
pybind11_add_module(nns_search ${SOURCES})
