#include <algorithm>
#include <queue>
#include <set>
#include <unordered_set>
#include <algorithm>
#include <ctime>
#include <random>
#include <unordered_map>
#include <iostream>
using namespace std;
class vector {
public:
    vector() : size(0), capacity(10) {
        data = new double[capacity];
    }

    ~vector() {
        delete[] data;
    }

    void push_back(double value) {
        if (size >= capacity) {
            resize();
        }
        data[size++] = value;
    }

    double& operator[](int index) {
        return data[index];
    }

    int getSize() const {
        return size;
    }

private:
    double* data;
    int size;
    int capacity;

    void resize() {
        capacity *= 2;
        double* newData = new double[capacity];
        for (int i = 0; i < size; i++) {
            newData[i] = data[i];
        }
        delete[] data;
        data = newData;
    }
};


struct Item {
	Item(vector<double> _values):values(_values) {}
	vector<double> values;
	// Assume L2 distance
	double dist(Item& other) {
		double result = 0.0;
		for (int i = 0; i < values.size(); i++) result += (values[i] - other.values[i]) * (values[i] - other.values[i]);
		return result;
	}
};

struct HNSWGraph {
	HNSWGraph(int _M, int _MMax, int _MMax0, int _efConstruction, int _ml):M(_M),MMax(_MMax),MMax0(_MMax0),efConstruction(_efConstruction),ml(_ml){
		layerEdgeLists.push_back(unordered_map<int, vector<int>>());
	}
	
	// Number of neighbors
	int M;
	// Max number of neighbors in layers >= 1
	int MMax;
	// Max number of neighbors in layers 0
	int MMax0;
	// Search numbers in construction
	int efConstruction;
	// Max number of layers
	int ml;

	// number of items
	int itemNum;
	// actual vector of the items
	vector<Item> items;
	// adjacent edge lists in each layer
	vector<unordered_map<int, vector<int>>> layerEdgeLists;
	// enter node id
	int enterNode;

	default_random_engine generator;

	// methods
	void addEdge(int st, int ed, int lc);
	vector<int> searchLayer(Item& q, int ep, int ef, int lc);
	void Insert(Item& q);
	vector<int> KNNSearch(Item& q, int K);

	void printGraph() {
		for (int l = 0; l < layerEdgeLists.size(); l++) {
			cout << "Layer:" << l << endl;
			for (auto it = layerEdgeLists[l].begin(); it != layerEdgeLists[l].end(); ++it) {
				cout << it->first << ":";
				for (auto ed: it->second) cout << ed << " ";
				cout << endl;
			}
		}
	}
};



vector<int> HNSWGraph::searchLayer(Item& q, int ep, int ef, int lc) {
	set<pair<double, int>> candidates;
	set<pair<double, int>> nearestNeighbors;
	unordered_set<int> isVisited;

	double td = q.dist(items[ep]);
	candidates.insert(make_pair(td, ep));
	nearestNeighbors.insert(make_pair(td, ep));
	isVisited.insert(ep);
	while (!candidates.empty()) {
		auto ci = candidates.begin(); candidates.erase(candidates.begin());
		int nid = ci->second;
		auto fi = nearestNeighbors.end(); fi--;
		if (ci->first > fi->first) break;
		for (int ed: layerEdgeLists[lc][nid]) {
			if (isVisited.find(ed) != isVisited.end()) continue;
			fi = nearestNeighbors.end(); fi--;
			isVisited.insert(ed);
			td = q.dist(items[ed]);
			if ((td < fi->first) || nearestNeighbors.size() < ef) {
				candidates.insert(make_pair(td, ed));
				nearestNeighbors.insert(make_pair(td, ed));
				if (nearestNeighbors.size() > ef) nearestNeighbors.erase(fi);
			}
		}
	}
	vector<int> results;
	for(auto &p: nearestNeighbors) results.push_back(p.second);
	return results;
}

vector<int> HNSWGraph::KNNSearch(Item& q, int K) {
	int maxLyer = layerEdgeLists.size() - 1;
	int ep = enterNode;
	for (int l = maxLyer; l >= 1; l--) ep = searchLayer(q, ep, 1, l)[0];
	return searchLayer(q, ep, K, 0);
}

void HNSWGraph::addEdge(int st, int ed, int lc) {
	if (st == ed) return;
	layerEdgeLists[lc][st].push_back(ed);
	layerEdgeLists[lc][ed].push_back(st);
}

void HNSWGraph::Insert(Item& q) {
	int nid = items.size();
	itemNum++; items.push_back(q);
	// sample layer
	int maxLyer = layerEdgeLists.size() - 1;
	int l = 0;
	uniform_real_distribution<double> distribution(0.0,1.0);
	while(l < ml && (1.0 / ml <= distribution(generator))) {
		l++;
		if (layerEdgeLists.size() <= l) layerEdgeLists.push_back(unordered_map<int, vector<int>>());
	}
	if (nid == 0) {
		enterNode = nid;
		return;
	}
	// search up layer entrance
	int ep = enterNode;
	for (int i = maxLyer; i > l; i--) ep = searchLayer(q, ep, 1, i)[0];
	for (int i = min(l, maxLyer); i >= 0; i--) {
		int MM = l == 0 ? MMax0 : MMax;
		vector<int> neighbors = searchLayer(q, ep, efConstruction, i);
		vector<int> selectedNeighbors = vector<int>(neighbors.begin(), neighbors.begin()+min(int(neighbors.size()), M));
		for (int n: selectedNeighbors) addEdge(n, nid, i);
		for (int n: selectedNeighbors) {
			if (layerEdgeLists[i][n].size() > MM) {
				vector<pair<double, int>> distPairs;
				for (int nn: layerEdgeLists[i][n]) distPairs.emplace_back(items[n].dist(items[nn]), nn);
				sort(distPairs.begin(), distPairs.end());
				layerEdgeLists[i][n].clear();
				for (int d = 0; d < min(int(distPairs.size()), MM); d++) layerEdgeLists[i][n].push_back(distPairs[d].second);
			}
		}
		ep = selectedNeighbors[0];
	}
	if (l == layerEdgeLists.size() - 1) enterNode = nid;
}


int main() {
	freopen("input.txt", "r", stdin);
	int n, K, d, q;
	cin >> n >> d>> K;
		default_random_engine generator;
	uniform_real_distribution<double> distribution(0.0,1.0);
	vector<Item> randomItems;
	for (int i = 0; i < n; i++) {
		vector<double> temp(d);
		for (int d = 0; d < d; d++) {
			cin >> temp[d];
		}
		randomItems.emplace_back(temp);
	}
	random_shuffle(randomItems.begin(), randomItems.end());

	// construct graph
	HNSWGraph myHNSWGraph(10, 30, 30, 10, 2);
	for (int i = 0; i < n; i++) {
		if (i % 10000 == 0) cout << i << endl;
		myHNSWGraph.Insert(randomItems[i]);
	}
	
	double total_brute_force_time = 0.0;
	double total_hnsw_time = 0.0;

	cin >> q;
	cout << "START QUERY" << endl;
	int numHits = 0;
	for (int i = 0; i < q; i++) {
		// Generate random query
		vector<double> temp(d);
		for (int d = 0; d < d; d++) {
			cin >> temp[d];
		}
		Item query(temp);

		// Brute force
		clock_t begin_time = clock();
		vector<pair<double, int>> distPairs;
		for (int j = 0; j < n; j++) {
			if (j == i) continue;
			distPairs.emplace_back(query.dist(randomItems[j]), j);
		}
		sort(distPairs.begin(), distPairs.end());
		total_brute_force_time += double( clock () - begin_time ) /  CLOCKS_PER_SEC;

		begin_time = clock();
		vector<int> knns = myHNSWGraph.KNNSearch(query, K);
		for(int i = 0; i < knns.size(); i++) {
			cout << knns[i] << " ";
		}
		cout << endl;
		total_hnsw_time += double( clock () - begin_time ) /  CLOCKS_PER_SEC;

		if (knns[0] == distPairs[0].second) numHits++;
	}
	cout << numHits << " " << total_brute_force_time / q  << " " << total_hnsw_time / q << endl;
	return 0;
}
