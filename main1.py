
# globals
# list islands (x, y, k)


class HashiGrid:
    def __init__(self, filename):
        self.n_size =0
        self.filename = filename
        self.n_islands =0
        self.island_coords = []
        self.digits =[]
        
        self.getInput()

    def getInput(self):
            with open(self.filename, "r") as f:
                k = f.readlines()   
                self.n_size = len(k)   
                for i in range(len(k)):
                    line = k[i].split()
                    for j in range(len(line)):
                        if line[j] != "0":
                            self.island_coords.append((i, j))
                            self.digits.append(int(line[j]))
            self.n_islands = len(self.island_coords)

    def printGrid(self):
        for i in range(len(self.island_coords)):
            print(f'Island {self.island_coords[i]} with bridges = {self.digits[i]}')


def adjacent_islands( h_grid, island_index):
    x, y = h_grid.island_coords[island_index]
    adj_islands = []
    for i in range(h_grid.n_islands):
        if i != island_index:
            x1, y1 = h_grid.island_coords[i]
            if x == x1 or y == y1:
                adj_islands.append(i)
    return adj_islands

def intersect(h_grid, ai, aj, bi, bj):
    coords_under_a, bridge_a_vertical = coordinates_between(h_grid, ai, aj)
    coords_under_b, bridge_b_vertical = coordinates_between(h_grid, bi, bj)

    if bridge_a_vertical != bridge_b_vertical
        return bool(set(coords_under_a) & set(coords_under_b))
    return False

def find_subtour(h_grid, solver, y_vars):
    bridges = {island: [] for island in range(h_grid.n_islands)}
    for bridge, var in y_vars.item():
        if solver.Value(var):
            i, j = bridge
            bridges[i].append[j]
            bridges[j].append[i]

    subtour_islands = {0}

    def scan(island):
        while bridges[island]:
            successor = bridges[island].pop(0)
            bridges[successor].remove(island)
            if successor not in subtour_islands:
                subtour_islands.add(successor)
                scan(successor)

    scan(0)
    
    if len(subtour_islands) != h_grid.n_islands:
        return subtour_islands
    return None

