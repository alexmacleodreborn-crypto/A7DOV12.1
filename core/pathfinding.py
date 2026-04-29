# core/pathfinding.py

import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(node, grid_size):
    x, y = node

    moves = [
        (x+1, y), (x-1, y),
        (x, y+1), (x, y-1)
    ]

    valid = []
    for nx, ny in moves:
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            valid.append((nx, ny))

    return valid


def a_star(start, goal, obstacles, grid_size):

    obstacles = set(tuple(o) for o in obstacles)

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:

        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(list(current))
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(current, grid_size):

            if neighbor in obstacles:
                continue

            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g

                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []  # no path found
