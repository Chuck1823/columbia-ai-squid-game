import numpy as np
import Grid


def manhattan_distance(position, target):
    return np.abs(target[0] - position[0]) + np.abs(target[1] - position[1])


def grid_copy_throw_trap(pos, grid_copy, intended_position):
    # find neighboring cells
    neighbors = grid_copy.get_neighbors(intended_position)

    neighbors = [neighbor for neighbor in neighbors if grid_copy.getCellValue(neighbor) <= 0]
    n = len(neighbors)

    probs = np.ones(1 + n)

    # compute probability of success, p
    p = 1 - 0.05 * (manhattan_distance(pos, intended_position) - 1)

    probs[0] = p

    probs[1:] = np.ones(len(neighbors)) * ((1 - p) / n)

    # add desired coordinates to neighbors
    neighbors.insert(0, intended_position)

    # return
    result = np.random.choice(np.arange(n + 1), p=probs)

    return neighbors[result]


def get_neighbors_by_level(pos, level):
    x, y = pos

    valid_range = lambda t: range(max(t - (1 + level), 0), min(t + (2 + level), 7))

    # find all neighbors
    neighbors = list({(a, b) for a in valid_range(x) for b in valid_range(y)} - {(x, y)})

    while level != -1:
        level -= 1
        valid_range = lambda t: range(max(t - (1 + level), 0), min(t + (2 + level), 7))

        # find all neighbors
        prev_lvl_neighbors = list({(a, b) for a in valid_range(x) for b in valid_range(y)} - {(x, y)})

        neighbors = [i for i in neighbors if i not in prev_lvl_neighbors]

    return neighbors


def check_if_trapped(lvl_ns, avail_cells):
    if any(item in avail_cells for item in lvl_ns):
        return False
    else:
        return True
