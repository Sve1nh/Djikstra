import pygame
import heapq
import math
import time # ### ИЗМЕНЕНИЕ: импортируем модуль time для задержки

# --- 1. ОПРЕДЕЛЕНИЕ ГРАФОВ И ИХ КООРДИНАТ ---
# (Остается без изменений)
GRAPH_1 = {
    'V1': {'V2': 5},
    'V2': {'V3': 1},
    'V3': {'V4': 3},
    'V4': {'V2': 6, 'V1' : 3},
    'V5': {'V1': 9, 'V3' : 1, 'V4' : 5},
}
POSITIONS_1 = {
    'V1': (100, 400), 'V4': (120, 250), 'V3': (300, 300),
    'V5': (50, 100), 'V2': (140, 350)
}

GRAPH_2 = {
    'S': {'A': 7, 'B': 2, 'C': 3}, 'A': {'S': 7, 'B': 3, 'D': 4},
    'B': {'S': 2, 'A': 3, 'D': 4, 'H': 1}, 'C': {'S': 3, 'L': 2},
    'D': {'A': 4, 'B': 4, 'F': 5}, 'H': {'B': 1, 'F': 3, 'G': 2},
    'G': {'H': 2, 'E': 2}, 'F': {'D': 5, 'H': 3}, 'L': {'C': 2, 'I': 4, 'J': 4},
    'I': {'L': 4, 'J': 6, 'K': 4}, 'J': {'L': 4, 'I': 6, 'K': 4},
    'K': {'I': 4, 'J': 4, 'E': 5}, 'E': {'G': 2, 'K': 5}
}
POSITIONS_2 = {
    'S': (150, 100), 'A': (300, 50), 'B': (300, 150), 'C': (150, 250),
    'D': (450, 100), 'H': (450, 200), 'G': (600, 250), 'F': (600, 150),
    'L': (150, 400), 'I': (300, 450), 'J': (300, 350), 'K': (450, 400),
    'E': (600, 350)
}

# --- 2. РЕАЛИЗАЦИЯ АЛГОРИТМА ДЕЙКСТРЫ С ВЫВОДОМ В КОНСОЛЬ ---

def dijkstra(graph, start_node, verbose=False):
    """
    Реализация алгоритма Дейкстры.
    verbose=True включает пошаговый вывод таблицы в консоль.
    """
    distances = {node: float('infinity') for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}
    priority_queue = [(0, start_node)]
    
    # ### ИЗМЕНЕНИЕ: Логика для печати таблицы в консоли ###
    if verbose:
        sorted_nodes = sorted(graph.keys())
        # Формируем заголовок таблицы
        header = f"{'Шаг':<5} | {'Вершина':<10} | " + " | ".join([f"d({node})" for node in sorted_nodes])
        print("\n--- Таблица работы алгоритма Дейкстры ---")
        print(header)
        print("-" * len(header))
    
    step = 0
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        if current_distance > distances[current_node]:
            continue

        # ### ИЗМЕНЕНИЕ: Печать текущего шага в таблицу ###
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
        print("--- Алгоритм завершен ---\n")
                
    return distances, predecessors

# Функция reconstruct_path остается без изменений
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

# --- 3. НАСТРОЙКИ PYGAME И ВИЗУАЛИЗАЦИИ ---
# ... (Константы и цвета остаются без изменений)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
NODE_RADIUS = 20
FONT_SIZE = 18
ARROW_SIZE = 15 # ### ИЗМЕНЕНИЕ: Увеличим размер стрелки

WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (200, 200, 200)
BLUE = (0, 0, 255); GREEN = (0, 255, 0); RED = (255, 0, 0); PURPLE = (128, 0, 128)

# --- 4. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОТРИСОВКИ ---

def draw_arrow(screen, color, start, end, width=2):
    """### ИЗМЕНЕНИЕ: Улучшенная функция для рисования стрелки."""
    # Вектор от начала к концу
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.sqrt(dx*dx + dy*dy)
    
    if length == 0: return # Не рисовать, если точки совпадают
    
    # Нормализуем вектор
    udx, udy = dx / length, dy / length
    
    # Новая конечная точка линии, смещенная на радиус вершины
    new_end_x = end[0] - udx * (NODE_RADIUS + 2)
    new_end_y = end[1] - udy * (NODE_RADIUS + 2)
    
    pygame.draw.line(screen, color, start, (new_end_x, new_end_y), width)
    
    # Рисуем наконечник стрелки
    angle = math.atan2(dy, dx)
    p1 = (new_end_x - ARROW_SIZE * math.cos(angle - math.pi/6), new_end_y - ARROW_SIZE * math.sin(angle - math.pi/6))
    p2 = (new_end_x - ARROW_SIZE * math.cos(angle + math.pi/6), new_end_y - ARROW_SIZE * math.sin(angle + math.pi/6))
    pygame.draw.polygon(screen, color, [(new_end_x, new_end_y), p1, p2])

# Функция draw_graph остается почти без изменений
def draw_graph(screen, font, graph, positions, selected_start, highlighted_path):
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            start_pos = positions[node]
            end_pos = positions[neighbor]
            is_path_edge = False
            if highlighted_path:
                for i in range(len(highlighted_path) - 1):
                    if (highlighted_path[i] == node and highlighted_path[i+1] == neighbor):
                        is_path_edge = True
                        break
            edge_color = RED if is_path_edge else GRAY
            edge_width = 4 if is_path_edge else 2
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

# Функция get_node_at_pos остается без изменений
def get_node_at_pos(positions, pos):
    for node, node_pos in positions.items():
        if math.sqrt((node_pos[0] - pos[0])**2 + (node_pos[1] - pos[1])**2) <= NODE_RADIUS:
            return node
    return None

# --- 5. ГЛАВНЫЙ ЦИКЛ ПРОГРАММЫ ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Визуализация алгоритма Дейкстры")
    font = pygame.font.Font(None, FONT_SIZE)
    info_font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()

    graphs = [(GRAPH_1, POSITIONS_1), (GRAPH_2, POSITIONS_2)]
    current_graph_index = 0
    current_graph, current_positions = graphs[current_graph_index]

    start_node = None
    end_node = None
    shortest_path = None
    path_info = ""

    button_rect = pygame.Rect(SCREEN_WIDTH - 160, 10, 150, 40)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    current_graph_index = (current_graph_index + 1) % len(graphs)
                    current_graph, current_positions = graphs[current_graph_index]
                    start_node = None; end_node = None; shortest_path = None; path_info = ""
                    continue

                clicked_node = get_node_at_pos(current_positions, event.pos)
                if clicked_node:
                    if not start_node:
                        start_node = clicked_node
                        shortest_path = None
                        path_info = f"Выбрана начальная вершина: {start_node}. Выберите конечную."
                    elif not end_node and clicked_node != start_node: # Убедимся, что конечная вершина не та же, что и начальная
                        end_node = clicked_node
                        
                        # ### ИЗМЕНЕНИЕ: Запускаем алгоритм с выводом в консоль ###
                        print(f"\nЗапуск поиска пути от '{start_node}' до '{end_node}'...")
                        distances, predecessors = dijkstra(current_graph, start_node, verbose=True)
                        
                        # ### ИЗМЕНЕНИЕ: Имитация задержки ###
                        time.sleep(1.5) # Пауза в полсекунды
                        
                        path = reconstruct_path(predecessors, start_node, end_node)
                        
                        if path:
                            shortest_path = path
                            path_info = f"Путь от {start_node} до {end_node}: {' -> '.join(path)}. Длина: {distances[end_node]}"
                        else:
                            shortest_path = None
                            path_info = f"Путь от {start_node} до {end_node} не найден."
                        
                        start_node = None
                        end_node = None

        # Отрисовка
        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        btn_text = info_font.render(f"Сменить граф", True, BLACK)
        screen.blit(btn_text, (button_rect.x + 15, button_rect.y + 10))
        draw_graph(screen, font, current_graph, current_positions, start_node, shortest_path)
        info_text = "Выберите начальную вершину." if not start_node and not path_info else path_info
        info_surface = info_font.render(info_text, True, BLACK)
        screen.blit(info_surface, (10, 10))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()