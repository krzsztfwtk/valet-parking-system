from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QTimer
import time
import parking_space

def parking_spaces_to_ids(parking_spaces):
    return [
        [space.car.id if space.car is not None else None for space in row]
        for row in parking_spaces
    ]

def move_car_to_destination(parking_spaces, destination, id):
    start_state = parking_spaces_to_ids(parking_spaces)
    target_car_id = id

    start_time_calculation = time.time()
    moves = a_star_parking(start_state, target_car_id, destination)
    end_time_calculation = time.time()
    elapsed_time_calculation = end_time_calculation - start_time_calculation
    print(f"Elapsed time for Python version: {elapsed_time_calculation} seconds")

    return moves, elapsed_time_calculation

def free_up_space(parking_spaces, target_coords):
    start_state = parking_spaces_to_ids(parking_spaces)

    start_time = time.time()

    moves = a_star_parking(start_state, None, target_coords, is_final_state_func=is_space_free)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time for freeing up space: {elapsed_time} seconds")

    for move in moves:
        direction, (src_x, src_y), (dest_x, dest_y) = move

        if direction == 'right':
            parking_spaces[src_x][src_y].car.move_right()
        elif direction == 'up':
            parking_spaces[src_x][src_y].car.move_up()
        elif direction == 'left':
            parking_spaces[src_x][src_y].car.move_left()
        elif direction == 'down':
            parking_spaces[src_x][src_y].car.move_down()

    return moves


def is_final_parking_state(state, car_id, dest_coords):
    x, y = dest_coords
    return state[x][y] is not None and state[x][y] == car_id

def is_space_free(state, _, dest_coords):
    x, y = dest_coords
    return state[x][y] is None

def create_all_parking_neighbors_states(state):
    neighbors = []
    for x in range(len(state)):
        for y in range(len(state[x])):
            if state[x][y] is not None:
                for dx, dy, move in [(1, 0, 'right'), (-1, 0, 'left'), (0, 1, 'down'), (0, -1, 'up')]:
                    new_x, new_y = x + dx, y + dy
                    if 0 <= new_x < len(state) and 0 <= new_y < len(state[0]) and state[new_x][new_y] is None:
                        new_state = [row.copy() for row in state]
                        new_state[x][y], new_state[new_x][new_y] = None, new_state[x][y]
                        neighbors.append((new_state, move, (x, y), (new_x, new_y)))
    return neighbors

def a_star_parking(start_state, car_id, dest_coords, is_final_state_func=is_final_parking_state):
    open_list = [(start_state, [], 0)]
    closed_list = []

    while open_list:
        open_list.sort(key=lambda x: x[2])
        current_state, current_moves, current_g = open_list.pop(0)
        closed_list.append(current_state)

        if is_final_state_func(current_state, car_id, dest_coords):
            return current_moves

        for neighbor, move_direction, src_coords, new_coords in create_all_parking_neighbors_states(current_state):
            if neighbor in closed_list:
                continue

            new_moves = current_moves + [(move_direction, src_coords, new_coords)]
            new_g = current_g + 1

            open_list.append((neighbor, new_moves, new_g))
