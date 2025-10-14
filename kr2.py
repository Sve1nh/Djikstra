import pygame
import math
import tkinter as tk
from tkinter import filedialog

# --- Класс для представления графа и преобразований ---

class Graph:
    def __init__(self):
        self.adj_list = {}
        self.num_vertices = 0

    def _update_num_vertices(self):
        if not self.adj_list:
            self.num_vertices = 0
            return
        all_nodes = set(self.adj_list.keys())
        for neighbors in self.adj_list.values():
            all_nodes.update(neighbors.keys())
        self.num_vertices = max(all_nodes) + 1 if all_nodes else 0
    
    # --- Преобразования ИЗ других форматов ВО внутренний (список смежности) ---

    def from_matrix(self, matrix):
        self.adj_list.clear()
        self.num_vertices = len(matrix)
        for i in range(self.num_vertices):
            for j in range(self.num_vertices):
                if matrix[i][j] != 0:
                    if i not in self.adj_list:
                        self.adj_list[i] = {}
                    self.adj_list[i][j] = matrix[i][j]
        self._update_num_vertices()

    def from_edge_list(self, edge_list, num_vertices):
        self.adj_list.clear()
        self.num_vertices = num_vertices
        for u, v, weight in edge_list:
            u_zero, v_zero = u - 1, v - 1
            if u_zero not in self.adj_list:
                self.adj_list[u_zero] = {}
            self.adj_list[u_zero][v_zero] = weight
        self._update_num_vertices()
        
    # --- Преобразования ИЗ внутреннего формата В другие ---
    
    def to_matrix(self):
        matrix = [[0] * self.num_vertices for _ in range(self.num_vertices)]
        for u, neighbors in self.adj_list.items():
            for v, weight in neighbors.items():
                if u < self.num_vertices and v < self.num_vertices:
                    matrix[u][v] = weight
        return matrix

    def to_edge_list(self):
        edge_list = []
        for u, neighbors in self.adj_list.items():
            for v, weight in neighbors.items():
                edge_list.append((u + 1, v + 1, weight))
        return sorted(edge_list)
        
    # --- Методы для работы с файлами и строковыми представлениями ---
    
    def load_from_file(self, filepath, format_type):
        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                if format_type == 'matrix':
                    num_v = int(lines[0])
                    matrix = [list(map(int, line.split())) for line in lines[1:]]
                    if len(matrix) != num_v: raise ValueError("Matrix dimensions mismatch")
                    self.from_matrix(matrix)
                elif format_type == 'edge_list':
                    num_v, num_e = map(int, lines[0].split())
                    edges = [tuple(map(int, line.split())) for line in lines[1:]]
                    if len(edges) != num_e: raise ValueError("Edge count mismatch")
                    self.from_edge_list(edges, num_v)
                elif format_type == 'adj_list':
                    self.adj_list.clear()
                    num_v = int(lines[0])
                    self.num_vertices = num_v
                    for i, line in enumerate(lines[1:]):
                        parts = list(map(int, line.split()))
                        num_neighbors = parts[0]
                        if num_neighbors > 0:
                            self.adj_list[i] = {}
                            for j in range(num_neighbors):
                                neighbor, weight = parts[1 + 2*j], parts[2 + 2*j]
                                self.adj_list[i][neighbor - 1] = weight
                    self._update_num_vertices()
            return True, f"Граф успешно загружен из {filepath.split('/')[-1]}"
        except Exception as e:
            self.adj_list.clear()
            self.num_vertices = 0
            return False, f"Ошибка загрузки файла: {e}"

    def get_string_representation(self, format_type):
        if self.num_vertices == 0:
            return "Граф пуст."
        if format_type == 'matrix':
            matrix = self.to_matrix()
            header = f"{self.num_vertices}\n"
            return header + "\n".join(" ".join(map(str, row)) for row in matrix)
        elif format_type == 'edge_list':
            edges = self.to_edge_list()
            header = f"{self.num_vertices} {len(edges)}\n"
            return header + "\n".join(f"{u} {v} {w}" for u, v, w in edges)
        elif format_type == 'adj_list':
            header = f"{self.num_vertices}\n"
            lines = []
            for i in range(self.num_vertices):
                if i in self.adj_list:
                    neighbors = self.adj_list[i]
                    line = f"{len(neighbors)}"
                    for neighbor, weight in sorted(neighbors.items()):
                        line += f"   {neighbor + 1} {weight}"
                    lines.append(line)
                else:
                    lines.append("0")
            return header + "\n".join(lines)
        return ""

    def save_to_file(self, filepath, format_type):
        try:
            with open(filepath, 'w') as f:
                f.write(self.get_string_representation(format_type))
            return True, f"Граф успешно сохранен в {filepath.split('/')[-1]}"
        except Exception as e:
            return False, f"Ошибка сохранения файла: {e}"


# --- Настройки и компоненты Pygame ---

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
FONT = pygame.font.Font(None, 24)
FONT_BOLD = pygame.font.Font(None, 28)

WHITE = (255, 255, 255); BLACK = (0, 0, 0); GRAY = (200, 200, 200)
BLUE = (0, 100, 255); RED = (255, 50, 50); PURPLE = (128, 0, 128)
LIGHT_GRAY = (220, 220, 220); DARK_GRAY = (100, 100, 100)

class Button:
    def __init__(self, rect, text, color=LIGHT_GRAY, text_color=BLACK):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2)
        text_surf = FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_text_area(screen, text, rect, title):
    pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, DARK_GRAY, rect, 2)
    
    title_surf = FONT_BOLD.render(title, True, BLACK)
    screen.blit(title_surf, (rect.x + 10, rect.y + 10))

    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_surf = FONT.render(line, True, BLACK)
        screen.blit(line_surf, (rect.x + 15, rect.y + 45 + i * 25))

def draw_visual_graph(screen, graph, area_rect):
    if graph.num_vertices == 0:
        return
    
    center_x, center_y = area_rect.center
    radius = min(area_rect.width, area_rect.height) // 2 - 50
    positions = {}
    angle_step = 2 * math.pi / graph.num_vertices
    for i in range(graph.num_vertices):
        angle = i * angle_step - math.pi / 2
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[i] = (int(x), int(y))

    for u, neighbors in graph.adj_list.items():
        for v, weight in neighbors.items():
            start_pos, end_pos = positions.get(u), positions.get(v)
            if start_pos and end_pos:
                draw_arrow(screen, DARK_GRAY, start_pos, end_pos, str(weight))

    for i in range(graph.num_vertices):
        pos = positions.get(i)
        if pos:
            pygame.draw.circle(screen, BLUE, pos, 20)
            pygame.draw.circle(screen, BLACK, pos, 20, 2)
            text_surf = FONT_BOLD.render(str(i + 1), True, WHITE)
            screen.blit(text_surf, text_surf.get_rect(center=pos))

def draw_arrow(screen, color, start, end, text, width=2):
    node_radius = 20
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = math.hypot(dx, dy)
    if length == 0: return
    
    udx, udy = dx / length, dy / length
    new_end = (end[0] - udx * (node_radius + 2), end[1] - udy * (node_radius + 2))
    
    pygame.draw.line(screen, color, start, new_end, width)
    
    angle = math.atan2(dy, dx)
    arrow_size = 15
    p1 = (new_end[0] - arrow_size * math.cos(angle - math.pi/6), new_end[1] - arrow_size * math.sin(angle - math.pi/6))
    p2 = (new_end[0] - arrow_size * math.cos(angle + math.pi/6), new_end[1] - arrow_size * math.sin(angle + math.pi/6))
    pygame.draw.polygon(screen, color, [new_end, p1, p2])

    mid_pos = (start[0]*0.4 + end[0]*0.6, start[1]*0.4 + end[1]*0.6)
    weight_surf = FONT.render(text, True, PURPLE)
    screen.blit(weight_surf, weight_surf.get_rect(center=mid_pos))


# --- Основной цикл приложения ---

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Графический Конвертер Представлений Графа")
    clock = pygame.time.Clock()

    graph = Graph()
    current_format = 'matrix'
    status_message = "Загрузите граф из файла или преобразуйте существующий."

    text_area_rect = pygame.Rect(20, 20, 360, 660)
    graph_area_rect = pygame.Rect(400, 20, 780, 660)

    buttons = {
        "load_matrix": Button((1060, 30, 120, 35), "Загрузить МС"),
        "load_edges":  Button((1060, 75, 120, 35), "Загрузить СР"),
        "load_adj":    Button((1060, 120, 120, 35), "Загрузить СС"),
        
        "save_matrix": Button((1060, 185, 120, 35), "Сохранить МС"),
        "save_edges":  Button((1060, 230, 120, 35), "Сохранить СР"),
        "save_adj":    Button((1060, 275, 120, 35), "Сохранить СС"),

        "conv_matrix": Button((1060, 340, 120, 35), "В МС"),
        "conv_edges":  Button((1060, 385, 120, 35), "В СР"),
        "conv_adj":    Button((1060, 430, 120, 35), "В СС"),
    }
    
    root = tk.Tk()
    root.withdraw()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if buttons["load_matrix"].is_clicked(pos):
                    filepath = filedialog.askopenfilename(title="Выберите файл матрицы смежности", filetypes=[("Text files", "*.txt")])
                    if filepath:
                        success, status_message = graph.load_from_file(filepath, 'matrix')
                        current_format = 'matrix' if success else current_format
                
                elif buttons["load_edges"].is_clicked(pos):
                    filepath = filedialog.askopenfilename(title="Выберите файл списка ребер", filetypes=[("Text files", "*.txt")])
                    if filepath:
                        success, status_message = graph.load_from_file(filepath, 'edge_list')
                        current_format = 'edge_list' if success else current_format

                elif buttons["load_adj"].is_clicked(pos):
                    filepath = filedialog.askopenfilename(title="Выберите файл списка смежности", filetypes=[("Text files", "*.txt")])
                    if filepath:
                        success, status_message = graph.load_from_file(filepath, 'adj_list')
                        current_format = 'adj_list' if success else current_format

                elif buttons["save_matrix"].is_clicked(pos) and graph.num_vertices > 0:
                    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Сохранить как матрицу смежности")
                    if filepath:
                        _, status_message = graph.save_to_file(filepath, 'matrix')

                elif buttons["save_edges"].is_clicked(pos) and graph.num_vertices > 0:
                    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Сохранить как список ребер")
                    if filepath:
                        _, status_message = graph.save_to_file(filepath, 'edge_list')
                
                elif buttons["save_adj"].is_clicked(pos) and graph.num_vertices > 0:
                    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")], title="Сохранить как список смежности")
                    if filepath:
                        _, status_message = graph.save_to_file(filepath, 'adj_list')

                elif buttons["conv_matrix"].is_clicked(pos):
                    current_format = 'matrix'
                    status_message = "Граф преобразован в матрицу смежности."
                elif buttons["conv_edges"].is_clicked(pos):
                    current_format = 'edge_list'
                    status_message = "Граф преобразован в список ребер."
                elif buttons["conv_adj"].is_clicked(pos):
                    current_format = 'adj_list'
                    status_message = "Граф преобразован в список смежности."

        screen.fill(GRAY)
        
        pygame.draw.rect(screen, WHITE, graph_area_rect)
        draw_visual_graph(screen, graph, graph_area_rect)

        format_titles = {
            'matrix': 'Матрица смежности',
            'edge_list': 'Список ребер',
            'adj_list': 'Список смежности'
        }
        text_to_display = graph.get_string_representation(current_format)
        draw_text_area(screen, text_to_display, text_area_rect, format_titles[current_format])
        
        for btn in buttons.values():
            btn.draw(screen)

        status_surf = FONT.render(status_message, True, BLACK)
        screen.blit(status_surf, (410, SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()