import pygame
import time
import random
from collections import deque
import heapq

WIDTH, HEIGHT = 310, 600
TILE_SIZE = WIDTH // 3
FONT_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

GOAL_STATE = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
#START_STATE = [[2, 6, 5], [0, 8, 7], [4, 3, 1]]
START_STATE = [[1, 5, 2], [4, 0, 3], [7, 8, 6]]

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def is_valid(x, y):
    return 0 <= x < 3 and 0 <= y < 3

def swap_positions(state, x1, y1, x2, y2):
    new_state = [row[:] for row in state]
    new_state[x1][y1], new_state[x2][y2] = new_state[x2][y2], new_state[x1][y1]
    return new_state

def draw_board(screen, state, highlight=None, elapsed_time=None):
    screen.fill(WHITE)
    font = pygame.font.Font(None, FONT_SIZE)
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                color = GRAY if highlight != (i, j) else RED
                pygame.draw.rect(screen, color, (j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=(j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2))
                screen.blit(text, text_rect)
            
    buttons = ["BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Simple", "Steepest", "Stochastic", "Beam", "Simulated", "Min-conf"]
    for idx, btn in enumerate(buttons):
        pygame.draw.rect(screen, BLUE, (10 + (idx % 4) * 75, 320 + (idx // 4) * 55, 70, 50))
        text = font.render(btn, True, WHITE)
        screen.blit(text, (15 + (idx % 4) * 75, 335 + (idx // 4) * 55))

    if elapsed_time is not None:
        font = pygame.font.Font(None, 24)
        if elapsed_time < 0.001:
            text = font.render(f"Time: {elapsed_time * 1_000_000:.0f} µs", True, BLACK)
        elif elapsed_time < 1:
            text = font.render(f"Time: {elapsed_time * 1000:.1f} ms", True, BLACK)
        else:
            text = font.render(f"Time: {elapsed_time:.3f} s", True, BLACK)

        screen.blit(text, (10, 280))


    pygame.draw.rect(screen, BLUE, (120, 520, 80, 50))

    text = font.render("Reset", True, WHITE)
    screen.blit(text, (130, 535))

def bfs(start_state):
    queue = deque([(start_state, [])])
    visited = set()
    while queue:
        state, path = queue.popleft()
        if state == GOAL_STATE:
            return path
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        x, y = find_blank(state)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(state, x, y, nx, ny)
                queue.append((new_state, path + [new_state]))
    return None

def dfs_recursive(state, path, visited, depth_limit):
    if state == GOAL_STATE:
        return path
    if len(path) >= depth_limit:
        return None
    state_tuple = tuple(map(tuple, state))
    if state_tuple in visited:
        return None
    visited.add(state_tuple)
    x, y = find_blank(state)
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny):
            new_state = swap_positions(state, x, y, nx, ny)
            result = dfs_recursive(new_state, path + [new_state], visited, depth_limit)
            if result:
                return result
    return None

def dfs(start_state):
    return dfs_recursive(start_state, [], set(), 20)

def ids(start_state):
    depth = 0
    while True:
        result = dfs_recursive(start_state, [], set(), depth)
        if result:
            return result
        depth += 1

def ucs(start_state):
    priority_queue = [(0, start_state, [])]
    visited = set()
    while priority_queue:
        cost, state, path = heapq.heappop(priority_queue)
        if state == GOAL_STATE:
            return path
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        x, y = find_blank(state)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(state, x, y, nx, ny)
                heapq.heappush(priority_queue, (cost + 1, new_state, path + [new_state]))
    return None

def heuristic(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                goal_x, goal_y = divmod(state[i][j] - 1, 3)
                distance += abs(goal_x - i) + abs(goal_y - j)
    return distance

def greedy(start_state):
    priority_queue = [(heuristic(start_state), start_state, [])]
    visited = set()
    while priority_queue:
        h, state, path = heapq.heappop(priority_queue)
        if state == GOAL_STATE:
            return path
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        x, y = find_blank(state)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(state, x, y, nx, ny)
                heapq.heappush(priority_queue, (heuristic(new_state), new_state, path + [new_state]))
    return None

def astar(start_state):
    priority_queue = [(heuristic(start_state), 0, start_state, [])]
    visited = set()
    while priority_queue:
        f, cost, state, path = heapq.heappop(priority_queue)
        if state == GOAL_STATE:
            return path
        state_tuple = tuple(map(tuple, state))
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        x, y = find_blank(state)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(state, x, y, nx, ny)
                g = cost + 1
                h = heuristic(new_state)
                heapq.heappush(priority_queue, (g + h, g, new_state, path + [new_state]))
    return None

def ida_star_recursive(state, path, g, threshold, visited):
    f = g + heuristic(state)
    if f > threshold:
        return f, None
    if state == GOAL_STATE:
        return -1, path
    min_threshold = float('inf')
    state_tuple = tuple(map(tuple, state))
    visited.add(state_tuple)
    x, y = find_blank(state)
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny):
            new_state = swap_positions(state, x, y, nx, ny)
            if tuple(map(tuple, new_state)) in visited:
                continue
            t, result = ida_star_recursive(new_state, path + [new_state], g + 1, threshold, visited)
            if result:
                return -1, result
            if t < min_threshold:
                min_threshold = t
    visited.remove(state_tuple)
    return min_threshold, None

def ida_star(start_state):
    threshold = heuristic(start_state)
    while True:
        t, result = ida_star_recursive(start_state, [], 0, threshold, set())
        if result:
            return result
        if t == float('inf'):
            return None
        threshold = t

def simple_hill_climbing(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        x, y = find_blank(current_state)
        best_state = current_state
        best_h = heuristic(current_state)
        improved = False
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(current_state, x, y, nx, ny)
                new_h = heuristic(new_state)
                if new_h < best_h:
                    best_state, best_h = new_state, new_h
                    improved = True
        if not improved:
            break
        current_state = best_state
        path.append(current_state)
    return path if current_state == GOAL_STATE else None

def steepest_ascent_hill_climbing(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        x, y = find_blank(current_state)
        best_states = []
        best_h = heuristic(current_state)
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(current_state, x, y, nx, ny)
                new_h = heuristic(new_state)
                if new_h < best_h:
                    best_states.append((new_h, new_state))
        if not best_states:
            break
        best_states.sort()
        current_state = best_states[0][1]
        path.append(current_state)
    return path if current_state == GOAL_STATE else None

def stochastic_hill_climbing(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        x, y = find_blank(current_state)
        neighbors = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(current_state, x, y, nx, ny)
                neighbors.append((heuristic(new_state), new_state))
        if not neighbors:
            break
        random.shuffle(neighbors)
        next_state = min(neighbors, key=lambda x: x[0])[1]
        if heuristic(next_state) >= heuristic(current_state):
            break
        current_state = next_state
        path.append(current_state)
    return path if current_state == GOAL_STATE else None

def beam_search(start_state, beam_width=2):
    from heapq import heappush, heappop
    queue = [(heuristic(start_state), start_state, [])]
    visited = set()
    while queue:
        next_queue = []
        for _ in range(min(beam_width, len(queue))):
            h, state, path = heappop(queue)
            if state == GOAL_STATE:
                return path
            state_tuple = tuple(map(tuple, state))
            if state_tuple in visited:
                continue
            visited.add(state_tuple)
            x, y = find_blank(state)
            for dx, dy in MOVES:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny):
                    new_state = swap_positions(state, x, y, nx, ny)
                    heappush(next_queue, (heuristic(new_state), new_state, path + [new_state]))
        queue = sorted(next_queue)[:beam_width]
    return None

def simulated_annealing(start_state, initial_temp=1000, cooling_rate=0.999, min_temp=0.001, max_steps=50000):
    import math
    current_state = [row[:] for row in start_state]
    path = [current_state]
    
    best_state = current_state
    best_path = path[:]
    best_h = heuristic(current_state)

    if current_state == GOAL_STATE:
        return path

    temperature = initial_temp
    steps = 0

    while temperature > min_temp and steps < max_steps:
        steps += 1
        x, y = find_blank(current_state)
        neighbors = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(current_state, x, y, nx, ny)
                neighbors.append(new_state)
        if not neighbors:
            break

        next_state = random.choice(neighbors)
        delta = heuristic(next_state) - heuristic(current_state)

        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current_state = next_state
            path.append(current_state)

            h = heuristic(current_state)
            if h < best_h:
                best_h = h
                best_state = current_state
                best_path = path[:]

            if current_state == GOAL_STATE:
                return path

        temperature *= cooling_rate

    return best_path if best_state == GOAL_STATE else None


def min_conflicts_search(start_state, max_steps=1000):
    current_state = [row[:] for row in start_state]
    path = [current_state]
    for _ in range(max_steps):
        if current_state == GOAL_STATE:
            return path
        x, y = find_blank(current_state)
        conflicts = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny):
                new_state = swap_positions(current_state, x, y, nx, ny)
                h = heuristic(new_state)
                conflicts.append((h, new_state))
        if not conflicts:
            break
        conflicts.sort()
        current_state = conflicts[0][1]
        path.append(current_state)
    return path if current_state == GOAL_STATE else None


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("8-Puzzle Solver")
    current_state = [row[:] for row in START_STATE]
    solution = None
    running = True
    solving = False
    step_index = 0
    algorithm = None

    while running:
        highlight = find_blank(current_state) if solving and solution and step_index < len(solution) else None
        draw_board(screen, current_state, highlight, elapsed_time if solution else None)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 320 <= y <= 370:
                    if 10 <= x <= 80:
                        algorithm = bfs
                    elif 85 <= x <= 155:
                        algorithm = dfs
                    elif 160 <= x <= 230:
                        algorithm = ids
                    elif 235 <= x <= 305:
                        algorithm = ucs
                elif 380 <= y <= 430:
                    if 10 <= x <= 80:
                        algorithm = greedy
                    elif 85 <= x <= 155:
                        algorithm = astar
                    elif 160 <= x <= 230:
                        algorithm = ida_star
                    elif 235 <= x <= 305:
                        algorithm =simple_hill_climbing
                elif 430 <= y <= 485:
                    if 10 <= x <= 80:
                        algorithm = steepest_ascent_hill_climbing
                    elif 85 <= x <= 155:
                        algorithm = stochastic_hill_climbing
                    elif 160 <= x <= 230:
                        algorithm = beam_search
                    elif 235 <= x <= 305:
                        algorithm = simulated_annealing
                elif 485 <= y <= 520:
                    if 10 <= x <= 80:
                        algorithm = min_conflicts_search

                elif 520 <= y <= 570 and 120 <= x <= 200:
                    current_state = [row[:] for row in START_STATE]
                    solution = None
                    solving = False
                    step_index = 0
                
                if algorithm:
                    start_time = time.time()
                    solution = algorithm(current_state)
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    if solution:
                        print("Solution:")
                        for step in solution:
                            for row in step:
                                print(row)
                            print("\n")
                        solving = True
                        step_index = 0
                    else:
                        print("No solution found.")
                    algorithm = None

        if solving and solution:
            if step_index < len(solution):
                current_state = solution[step_index]
                step_index += 1
                time.sleep(0.5)
            else:
                solving = False
    pygame.quit()

if __name__ == "__main__":
    main()
