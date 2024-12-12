# KNN Search Algorithms

This package provides a collection of K-Nearest Neighbors (KNN) search algorithms implemented in C++ and exposed to Python using pybind11.

## Included Algorithms

1. Brute Force Search - Basic exhaustive search
2. LSH (Locality Sensitive Hashing) - Approximate search using hash tables
3. HNSW (Hierarchical Navigable Small World) - Graph-based approximate search

## Requirements

- Python 3.6 or later
- C++ compiler with C++14 support
- CMake 3.10 or later
- pybind11

## Installation

1. Create and activate a conda environment:
```bash
conda create -n knn_search python=3.10
conda activate knn_search
```

2. Install pybind11:
```bash
conda install pybind11 cmake
```

3. Build and install the package:
```bash
python setup.py install
```

## Usage

```python
import numpy as np
from knn_search import brute_force_search, hash_search, hnsw_search

# Create some example data
vectors = np.random.rand(1000, 128).astype(np.float32)  # Database vectors
query = np.random.rand(128).astype(np.float32)          # Query vector
k = 5  # Number of nearest neighbors to find

# Use different search methods
brute_force_results = brute_force_search(vectors, query, k)
hash_results = hash_search(vectors, query, k)
hnsw_results = hnsw_search(vectors, query, k)
```

Each search function returns a list of indices corresponding to the k-nearest neighbors in the input vectors.
