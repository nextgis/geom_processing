from shapely.geometry import LineString


def is_free(line, polygons):
    """Checks if line intersects one or more polygon from list."""
    to_return = 1
    for poly in polygons:
        to_return = to_return and not poly.intersects(line)
    return to_return


def get_edges(i, j_b, e_full):
    """Returns edges of point i,j"""
    return {e_full[edge] for edge in e_full.keys
            if (i, j_b) in edge.key}


def find_common(e_j_b, e_j_e):
    """Finds vertexes, which can form a triangle with two other vertexes."""
    common = []
    for e_b in e_j_b:
        for e_e in e_j_e:
            inter = e_b.intersection(e_e)
            if len(inter) == 1:
                point = list(inter)[0]
                common.append(point)
    return common


def get_adjacent(edge, trs):
    """Returns triangles, which are adjacent for edge"""
    adj = []
    for tr in trs:
        if edge.key <= tr.key:
            adj.append(tr)
    return adj


def build_bridges(geoms, m):
    """Builds bridges-polygons between n polygons to save m polygons where m < n."""
    vertexes = [geom.exterior.coords for geom in geoms]  # vetrexes[i][j] - j-ая вершина в i-ом полигоне
    e_full = {}  # ребра: исходные и добавленные
    n = len(vertexes)
    for i in range(n):
        for j in range(len(vertexes[i])):
            j_e = j + 1
            if j_e == len(vertexes[i]):
                j_e = 0
            e_full[frozenset([(i, j), (i, j_e)])] = {"origin": "bound"}
    
    # 1. Построение отрезков
    for i_b in range(n - 1):
        for j_b in range(len(vertexes[i_b])):
            for i_e in range(i_b + 1, n):
                for j_e in range(len(vertexes[i_e])):
                    if is_free(LineString([vertexes[i_b][j_b], vertexes[i_e][j_e]]), geoms):
                        e_full[frozenset([(i_b, j_b), (i_e, j_e)])] = {"origin": "edge"}
    
    # 2. Сбор треугольников
    trs = {}
    for i in range(n - 1):
        for j_b in range(len(vertexes[i])):
            j_e = j_b + 1
            if j_e == len(vertexes[i]):
                j_e = 0
            e_j_b = get_edges(i, j_b, e_full)
            e_j_e = get_edges(i, j_e, e_full)
            common = find_common(e_j_b, e_j_e)
            for v in common:
                trs[frozenset([(i, j_b), (i, j_e), v])] = {"location": "out"}
                

"""
    Алгоритм построения перетяжек между полигонами
    с последующим объединением
    
    Дано:
    список p из n полигонов: 
        упорядоченные вершины v[i][j]
            i [0..n) - номер полигона
            j [0 .. len(v[i])) - номер вершины конкретного полигона
        информация о ребрах
            e[i][j] = (v[i][j], v[i][j + 1])
                i [0..n] - номер полигона
                j [0 .. len(v[i]) - 1] - номер ребра
    хотим m полигонов, m<n
                
    Найти:
        ребра, служащие границами для перетяжек между полигонами с наименьшей площадью
    
        перетяжка - четырехугольник(реже треугольник), 
            две стороны которого - ребра двух разных полигонов
    
    Шаги
        1.  Найти отрезки между вершинами разных полигонов,
            которые лежат вне полигонов
        2.  Собрать в список полученные треугольники 
            Одно ребро треугольника относится только к одному полигону
        3.  Какие из отрезков - оси перетяжек
                смотрим пару соседей ребра - треугольников
                в каждом должно быть по edge из двух разных полигонов
        4. проходка по перетяжкам
            берем площади соседних от оси треугольников, сортурием, ищем минимум
        5. объединение с перетяжкой
            добавляем треугольники с минимальной площадью вокруг оси перетяжки к будущему объединению
            ось перетяжки лишается своего статуса, это ребро внутри будущей геометрии
            в каждом из треульников изначально ребро полигона, ось перетяжки и третий отрезок
            третий отрезок становится одной из границ новой геометрии
        6. проверка не перетяжек на предмет того, попали ли они в класс перетяжек
            - добавить для третьих ребер, ставших границами
            - убрать для уже объединенных
            сохраняя порядок по площадям перетяжек
                если треугольник в будущем объединении, его площадь не учитываем при сортировке
            
        повторяем 5 - 6, пока не выполним n-m итераций    
        
        объединем перетяжки и полигоны в один полигон
"""