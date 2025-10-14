import pygame
import heapq
import math

GRAPH_1 = {
    'V1': {'V2': 5}, 'V2': {'V3': 1}, 'V3': {'V4': 3},
    'V4': {'V2': 6, 'V1' : 3}, 'V5': {'V1': 9, 'V3' : 1, 'V4' : 5},
}
POSITIONS_1 = {
    'V1': (100, 400), 'V4': (120, 250), 'V3': (300, 300),
    'V5': (50, 100), 'V2': (140, 350)
}

GRAPH_2 = {
    'B': {'A': 1, 'C': 2}, 'A' : {'D': 2}, 'E': {'A': 3}, 
    'C': {'A' : 5, 'D' : 3}, 'D': {'D' : 2, 'E':5,'C':1}
}
POSITIONS_2 = {
    'B': (100,100), 'A' : (200,140), 'E' : (400,120), 
    'C' : (150,230), 'D' : (300,220)
}

def dijkstra(graph, start_node, verbose=False):
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}
    priority_queue = [(0, start_node)]
    
    if verbose:
        sorted_nodes = sorted(graph.keys())
        header = f"{'Шаг':<5} | {'Вершина':<10} | " + " | ".join([f"d({node})" for node in sorted_nodes])
        print("\n--- Таблица работы алгоритма Дейкстры ---")
        print(header)
        print("-" * len(header))
    
    step = 0
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue

        if verbose:
            row = f"{step:<5} | {current_node:<10} | "
            dist_values = []
            for node in sorted_nodes:
                dist = distances[node]
                dist_str = "inf" if dist == float('infinity') else str(dist)
                dist_values.append(f"{dist_str:<5}")
            row += " | ".join(dist_values)
            print(row)
            step += 1
            
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
                
    if verbose:
        print("-" * len(header))
        print("--- Алгоритм Дейкстры завершен ---\n")
                
    return distances, predecessors

def reconstruct_path(predecessors, start_node, end_node):
    path = []
    current_node = end_node
    while current_node is not None:
        path.append(current_node)
        if current_node == start_node:
            break
        current_node = predecessors.get(current_node)
    
    if not path or path[-1] != start_node:
        return None
        
    return path[::-1]

def floyd_warshall(graph):
    nodes = sorted(list(graph.keys()))
    dist = {u: {v: float('inf') for v in nodes} for u in nodes}
    next_node = {u: {v: None for v in nodes} for u in nodes}

    for u in nodes:
        dist[u][u] = 0
        next_node[u][u] = u
        for v, weight in graph.get(u, {}).items():
            dist[u][v] = weight
            next_node[u][v] = v
            
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next_node[i][j] = next_node[i][k]
    
    print("\n--- Алгоритм Флойда-Уоршелла рассчитан для всех пар вершин ---")
    print("\n--- Матрица расстояний (dist) ---")
    header = "      " + " ".join([f"{node:<5}" for node in nodes])
    print(header)
    print("    -" + "-" * len(header))
    for i in nodes:
        row_str = f"{i:<5} |"
        for j in nodes:
            val = dist[i][j]
            row_str += f" {str(val) if val != float('inf') else 'inf':<5}"
        print(row_str)

    print("\n--- Матрица следующих вершин (next_node) ---")
    print(header)
    print("    -" + "-" * len(header))
    for i in nodes:
        row_str = f"{i:<5} |"
        for j in nodes:
            val = next_node[i][j]
            row_str += f" {str(val) if val is not None else 'N/A':<5}"
        print(row_str)

    return dist, next_node

def reconstruct_floyd_path(next_node, start, end):
    if next_node[start][end] is None:
        return None
    path = [start]
    current = start
    while current != end:
        current = next_node[current][end]
        if current is None:
            return None 
        path.append(current)
    return path

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NODE_RADIUS = 20
FONT_SIZE = 18
ARROW_SIZE = 15

WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (200, 200, 200)
BLUE = (0, 0, 255); GREEN = (0, 255, 0); RED = (255, 0, 0); PURPLE = (128, 0, 128)

def draw_arrow(screen, color, start, end, width=2):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx*dx + dy*dy)
    if length == 0: return 
    udx, udy = dx / length, dy / length
    new_end_x = end[0] - udx * (NODE_RADIUS + 2)
    new_end_y = end[1] - udy * (NODE_RADIUS + 2)
    pygame.draw.line(screen, color, start, (new_end_x, new_end_y), width)
    angle = math.atan2(dy, dx)
    p1 = (new_end_x - ARROW_SIZE * math.cos(angle - math.pi/6), new_end_y - ARROW_SIZE * math.sin(angle - math.pi/6))
    p2 = (new_end_x - ARROW_SIZE * math.cos(angle + math.pi/6), new_end_y - ARROW_SIZE * math.sin(angle + math.pi/6))
    pygame.draw.polygon(screen, color, [(new_end_x, new_end_y), p1, p2])

def draw_graph(screen, font, graph, positions, selected_start, highlighted_path):
    def draw_self_loop(screen, font, pos, weight, color, width):
        loop_radius = 15
        loop_center = (pos[0], pos[1] - NODE_RADIUS - loop_radius + 5)
        rect = pygame.Rect(loop_center[0] - loop_radius, loop_center[1] - loop_radius, 2 * loop_radius, 2 * loop_radius)
        pygame.draw.arc(screen, color, rect, math.radians(60), math.radians(350), width)
        angle = math.radians(60)
        arrow_tip_x = loop_center[0] + loop_radius * math.cos(angle)
        arrow_tip_y = loop_center[1] - loop_radius * math.sin(angle)
        p1 = (arrow_tip_x - ARROW_SIZE * math.cos(angle - math.pi/6), arrow_tip_y + ARROW_SIZE * math.sin(angle - math.pi/6))
        p2 = (arrow_tip_x - ARROW_SIZE * math.cos(angle + math.pi/6), arrow_tip_y + ARROW_SIZE * math.sin(angle + math.pi/6))
        pygame.draw.polygon(screen, color, [(arrow_tip_x, arrow_tip_y), p1, p2])
        weight_text = font.render(str(weight), True, PURPLE)
        screen.blit(weight_text, (loop_center[0] + loop_radius, loop_center[1] - loop_radius))

    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            start_pos = positions[node]
            is_path_edge = False
            if highlighted_path:
                for i in range(len(highlighted_path) - 1):
                    if (highlighted_path[i] == node and highlighted_path[i+1] == neighbor):
                        is_path_edge = True; break
            edge_color = RED if is_path_edge else GRAY
            edge_width = 4 if is_path_edge else 2

            if node == neighbor:
                draw_self_loop(screen, font, start_pos, weight, edge_color, edge_width)
            else:
                end_pos = positions[neighbor]
                is_bidirectional = neighbor in graph and node in graph.get(neighbor, {})
                if is_bidirectional and (neighbor, node) > (node, neighbor): continue
                
                if is_bidirectional:
                    pygame.draw.line(screen, edge_color, start_pos, end_pos, edge_width)
                    mid_pos_x = (start_pos[0] + end_pos[0]) / 2
                    mid_pos_y = (start_pos[1] + end_pos[1]) / 2
                    w1 = str(graph[node][neighbor]); w2 = str(graph[neighbor][node])
                    weight_text1 = font.render(f"{node}->{neighbor}: {w1}", True, PURPLE)
                    weight_text2 = font.render(f"{neighbor}->{node}: {w2}", True, PURPLE)
                    screen.blit(weight_text1, (mid_pos_x + 5, mid_pos_y - 15))
                    screen.blit(weight_text2, (mid_pos_x + 5, mid_pos_y + 5))
                else:
                    draw_arrow(screen, edge_color, start_pos, end_pos, edge_width)
                    mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
                    weight_text = font.render(str(weight), True, PURPLE)
                    screen.blit(weight_text, (mid_pos[0] + 5, mid_pos[1] + 5))
                
    for node, pos in positions.items():
        node_color = GREEN if node == selected_start else BLUE
        pygame.draw.circle(screen, node_color, pos, NODE_RADIUS)
        pygame.draw.circle(screen, BLACK, pos, NODE_RADIUS, 2)
        text = font.render(node, True, WHITE)
        text_rect = text.get_rect(center=pos)
        screen.blit(text, text_rect)

def get_node_at_pos(positions, pos):
    for node, node_pos in positions.items():
        if math.sqrt((node_pos[0] - pos[0])**2 + (node_pos[1] - pos[1])**2) <= NODE_RADIUS:
            return node
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Визуализация алгоритмов поиска кратчайшего пути")
    font = pygame.font.Font(None, FONT_SIZE)
    info_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    graphs = [(GRAPH_1, POSITIONS_1), (GRAPH_2, POSITIONS_2)]
    current_graph_index = 0
    current_graph, current_positions = graphs[current_graph_index]
    
    algorithms = ["Dijkstra", "Floyd-Warshall"]
    current_algorithm_index = 0
    
    floyd_distances = None
    floyd_next_nodes = None

    def precompute_floyd():
        nonlocal floyd_distances, floyd_next_nodes
        floyd_distances, floyd_next_nodes = floyd_warshall(current_graph)

    precompute_floyd()

    start_node = None
    end_node = None
    shortest_path = None
    path_info = ""

    graph_button_rect = pygame.Rect(SCREEN_WIDTH - 160, 10, 150, 40)
    algo_button_rect = pygame.Rect(SCREEN_WIDTH - 160, 60, 150, 40)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if graph_button_rect.collidepoint(event.pos):
                    current_graph_index = (current_graph_index + 1) % len(graphs)
                    current_graph, current_positions = graphs[current_graph_index]
                    start_node = None; end_node = None; shortest_path = None; path_info = ""
                    precompute_floyd()
                    continue
                
                if algo_button_rect.collidepoint(event.pos):
                    current_algorithm_index = (current_algorithm_index + 1) % len(algorithms)
                    start_node = None; end_node = None; shortest_path = None; path_info = ""
                    continue

                clicked_node = get_node_at_pos(current_positions, event.pos)
                if clicked_node:
                    if not start_node:
                        start_node = clicked_node
                        shortest_path = None
                        path_info = f"Выбрана начальная вершина: {start_node}. Выберите конечную."
                    elif not end_node and clicked_node != start_node:
                        end_node = clicked_node
                        selected_algorithm = algorithms[current_algorithm_index]
                        print(f"\nЗапуск поиска пути от '{start_node}' до '{end_node}' используя {selected_algorithm}...")
                        
                        path = None
                        distance = float('inf')

                        if selected_algorithm == "Dijkstra":
                            distances, predecessors = dijkstra(current_graph, start_node, verbose=True)
                            path = reconstruct_path(predecessors, start_node, end_node)
                            if end_node in distances:
                                distance = distances[end_node]
                        
                        elif selected_algorithm == "Floyd-Warshall":
                            path = reconstruct_floyd_path(floyd_next_nodes, start_node, end_node)
                            if start_node in floyd_distances and end_node in floyd_distances[start_node]:
                                distance = floyd_distances[start_node][end_node]
                            print("Результат взят из предварительно рассчитанной матрицы.")
                        
                        if path:
                            shortest_path = path
                            path_info = f"Путь от {start_node} до {end_node}: {' -> '.join(path)}. Длина: {distance}"
                        else:
                            shortest_path = None
                            path_info = f"Путь от {start_node} до {end_node} не найден."
                        
                        start_node = None
                        end_node = None

        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, graph_button_rect)
        pygame.draw.rect(screen, BLACK, graph_button_rect, 2)
        graph_btn_text = info_font.render(f"Сменить граф", True, BLACK)
        screen.blit(graph_btn_text, (graph_button_rect.x + 15, graph_button_rect.y + 10))

        pygame.draw.rect(screen, GRAY, algo_button_rect)
        pygame.draw.rect(screen, BLACK, algo_button_rect, 2)
        algo_btn_text = info_font.render(f"Алгоритм", True, BLACK)
        screen.blit(algo_btn_text, (algo_button_rect.x + 35, algo_button_rect.y + 10))

        draw_graph(screen, font, current_graph, current_positions, start_node, shortest_path)
        
        current_algo_name = algorithms[current_algorithm_index]
        algo_info_text = f"Алгоритм: {current_algo_name}"
        user_prompt_text = "Выберите начальную вершину." if not start_node and not path_info else path_info

        algo_surface = info_font.render(algo_info_text, True, BLACK)
        screen.blit(algo_surface, (10, 10))
        
        info_surface = info_font.render(user_prompt_text, True, BLACK)
        screen.blit(info_surface, (10, 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()