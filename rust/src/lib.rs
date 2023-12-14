use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::{BinaryHeap, HashSet};
use std::cmp::Ordering;

#[derive(Clone, Eq, PartialEq)]
struct State {
    board: Vec<Vec<i32>>,
    moves: Vec<(String, (usize, usize), (usize, usize))>,
    cost: i32,
}

impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        other.cost.cmp(&self.cost)
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[pyfunction]
fn a_star_parking_py(start_state: Vec<Vec<i32>>, car_id: i32, dest_coords: (usize, usize)) -> PyResult<Vec<(String, (usize, usize), (usize, usize))>> {
    let result = a_star_parking(start_state, car_id, dest_coords);
    Ok(result)
}

#[pymodule]
fn a_star_parking_module_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(a_star_parking_py, m)?)?;
    Ok(())
}


fn is_final_parking_state(state: &Vec<Vec<i32>>, car_id: i32, dest_coords: (usize, usize)) -> bool {
    state[dest_coords.0][dest_coords.1] == car_id
}

fn create_all_parking_neighbors_states(state: &Vec<Vec<i32>>) -> Vec<(Vec<Vec<i32>>, String, (usize, usize), (usize, usize))> {
    let mut neighbors = Vec::new();
    let directions = vec![
        (1, 0, "right"),
        (-1, 0, "left"),
        (0, 1, "down"),
        (0, -1, "up"),
    ];

    for (x, row) in state.iter().enumerate() {
        for (y, &val) in row.iter().enumerate() {
            if val != -1 {
                for &(dx, dy, dir) in &directions {
                    let new_x = (x as i32 + dx) as usize;
                    let new_y = (y as i32 + dy) as usize;
                    if new_x < state.len() && new_y < state[0].len() && state[new_x][new_y] == -1 {
                        let mut new_state = state.clone();
                        new_state[x][y] = -1;
                        new_state[new_x][new_y] = val;
                        neighbors.push((new_state, dir.to_string(), (x, y), (new_x, new_y)));
                    }
                }
            }
        }
    }

    neighbors
}

fn a_star_parking(start_state: Vec<Vec<i32>>, car_id: i32, dest_coords: (usize, usize)) -> Vec<(String, (usize, usize), (usize, usize))> {
    let mut open_list = BinaryHeap::new();
    open_list.push(State {
        board: start_state,
        moves: Vec::new(),
        cost: 0,
    });

    let mut closed_list = HashSet::new();

    while let Some(current) = open_list.pop() {
        let State { board, moves, cost } = current;

        if closed_list.contains(&board) {
            continue;
        }

        closed_list.insert(board.clone());

        if is_final_parking_state(&board, car_id, dest_coords) {
            return moves;
        }

        for (neighbor, move_direction, src_coords, new_coords) in create_all_parking_neighbors_states(&board) {
            if closed_list.contains(&neighbor) {
                continue;
            }
            let mut new_moves = moves.clone();
            new_moves.push((move_direction, src_coords, new_coords));
            let new_cost = cost + 1;
            open_list.push(State {
                board: neighbor,
                moves: new_moves,
                cost: new_cost,
            });
        }
    }

    Vec::new() // Return an empty vector if no solution found
}