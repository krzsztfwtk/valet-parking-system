#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <queue>
#include <tuple>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace std;

struct State {
    vector<vector<int>> board;
    vector<tuple<string, pair<int, int>, pair<int, int>>> moves;
    int cost;

    bool operator<(const State& other) const {
        return cost > other.cost;
    }
};

bool is_final_parking_state(const vector<vector<int>>& state, int car_id, pair<int, int> dest_coords) {
    return (state[dest_coords.first][dest_coords.second] == car_id);
}

vector<tuple<vector<vector<int>>, string, pair<int, int>, pair<int, int>>> create_all_parking_neighbors_states(const vector<vector<int>>& state) {
    vector<tuple<vector<vector<int>>, string, pair<int, int>, pair<int, int>>> neighbors;

    for (size_t x = 0; x < state.size(); ++x) {
        for (size_t y = 0; y < state[x].size(); ++y) {
            if (state[x][y] != -1) {
                vector<tuple<int, int, string>> directions = {{1, 0, "right"}, {-1, 0, "left"}, {0, 1, "down"}, {0, -1, "up"}};

                for (auto& [dx, dy, move] : directions) {
                    int new_x = x + dx;
                    int new_y = y + dy;
                    if (new_x >= 0 && new_x < static_cast<int>(state.size()) && new_y >= 0 && new_y < static_cast<int>(state[0].size()) && state[new_x][new_y] == -1) {
                        auto new_state = state;
                        new_state[x][y] = -1;
                        new_state[new_x][new_y] = state[x][y];
                        neighbors.push_back({new_state, move, {static_cast<int>(x), static_cast<int>(y)}, {new_x, new_y}});
                    }
                }
            }
        }
    }
    return neighbors;
}

vector<tuple<string, pair<int, int>, pair<int, int>>> a_star_parking(const vector<vector<int>>& start_state, int car_id, pair<int, int> dest_coords) {
    priority_queue<State> open_list;
    open_list.push({start_state, {}, 0});
    vector<vector<vector<int>>> closed_list;

    while (!open_list.empty()) {
        auto current = open_list.top();
        open_list.pop();
        auto current_state = current.board;
        auto current_moves = current.moves;
        auto current_cost = current.cost;

        closed_list.push_back(current_state);

        if (is_final_parking_state(current_state, car_id, dest_coords)) {
            return current_moves;
        }

        auto neighbors = create_all_parking_neighbors_states(current_state);
        for (auto& [neighbor, move_direction, src_coords, new_coords] : neighbors) {
            if (find(closed_list.begin(), closed_list.end(), neighbor) != closed_list.end()) {
                continue;
            }
            auto new_moves = current_moves;
            new_moves.push_back({move_direction, src_coords, new_coords});
            int new_cost = current_cost + 1;
            open_list.push({neighbor, new_moves, new_cost});
        }
    }
    return {}; // Return an empty vector if no solution found
}

namespace py = pybind11;

PYBIND11_MODULE(a_star_parking_module, m) {
    m.def("a_star_parking", &a_star_parking);
}



//pip install pybind11

//linux:
//g++ -O3 -Wall -shared -std=c++2a -fPIC $(python3 -m pybind11 --includes) a_star.cpp -o a_star_parking_module$(`python3 -config --extension-suffix`)

//windows:
//g++ -O3 -Wall -shared -std=c++2a -IC:\Users\krzys\AppData\Local\Programs\Python\Python310\include -IC:\Users\krzys\AppData\Local\Programs\Python\Python310\Lib\site-packages\pybind11\include a_star.cpp -L C:\Users\krzys\AppData\Local\Programs\Python\Python310\libs -lpython310 -o a_star_parking_module.dll

//g++ -O3 -Wall -shared -std=c++2a -fPIC -IC:\Users\krzys\AppData\Local\Programs\Python\Python310\Include -IC:\Users\krzys\AppData\Local\Programs\Python\Python310\lib\site-packages\pybind11\include a_star.cpp -o a_star_parking_module.pyd "-Wl,--export-all-symbols" -LC:\Users\krzys\AppData\Local\Programs\Python\Python310\libs -lpython310