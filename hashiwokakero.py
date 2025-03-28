from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4
from pysat.card import CardEnc
from itertools import combinations

class HashiGrid:
    def __init__(self, filename):
        self.n_size = 0
        self.filename = filename
        self.n_islands = 0
        self.island_coords = []
        self.digits = []
        
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

def adjacent_islands(h_grid, island_index):
    x, y = h_grid.island_coords[island_index]
    adj_islands = []
    
    min_dis = [1000000, 1000000, 1000000, 1000000]
    # top, left, bottom, right
    min_idx = [-1, -1, -1, -1]    

    for i in range(len(h_grid.island_coords)):
        x1, y1 = h_grid.island_coords[i]
        #find top neighbor
        if x1 < x and y1 == y:
            sub_min = abs(x1 - x)
            if sub_min < min_dis[0]:
                min_dis[0] = sub_min
                min_idx[0] = i
        #find left neighbor
        elif y1 < y and x1 == x:
            sub_min = abs(y1 - y)
            if sub_min < min_dis[1]:
                min_dis[1] = sub_min
                min_idx[1] = i
        #find bottom neighbor
        elif x1 > x and y1 == y:
            sub_min = abs(x1 - x)
            if sub_min < min_dis[2]:
                min_dis[2] = sub_min
                min_idx[2] = i
        #find right neighbor
        elif y1 > y and x1 == x:
            sub_min = abs(y1 - y)
            if sub_min < min_dis[3]:
                min_dis[3] = sub_min
                min_idx[3] = i
                
    for idx in min_idx:
        if (idx != -1):
            adj_islands.append(idx)
    
    return adj_islands            

def coordinates_between(h_grid, i, j):
    coordinates = [] 
    is_horizontal = None 
    
    # xet cau ngang
    if h_grid.island_coords[i][0] == h_grid.island_coords[j][0]: 
        x = h_grid.island_coords[i][0]
        coordinates = [
            (x, y)
            for y in range(
                min(h_grid.island_coords[i][1], h_grid.island_coords[j][1]) + 1, 
                max(h_grid.island_coords[i][1], h_grid.island_coords[j][1])
            )
        ]
        is_horizontal = True
    # xet cau doc
    elif h_grid.island_coords[i][1] == h_grid.island_coords[j][1]: 
        y = h_grid.island_coords[i][1]
        coordinates = [
            (x, y)
            for x in range(
                min(h_grid.island_coords[i][0], h_grid.island_coords[j][0]) + 1, 
                max(h_grid.island_coords[i][0], h_grid.island_coords[j][0])
            )
        ]
        is_horizontal = False
    return coordinates, is_horizontal 

def intersect(h_grid, ai, aj, bi, bj):
    coords_under_a, bridge_a_vertical = coordinates_between(h_grid, ai, aj)
    coords_under_b, bridge_b_vertical = coordinates_between(h_grid, bi, bj)

    if not coords_under_a or not coords_under_b:
        return False
    if bridge_a_vertical != bridge_b_vertical:
        return bool(set(coords_under_a) & set(coords_under_b))
    return False

def solve_hashi(filename):
    h_grid = HashiGrid(filename)
    idpool = IDPool()
    cnf = CNF()
    x_vars = {}

    # 1. Create bridge variables for each pair of adjacent islands
    for i in range(h_grid.n_islands):
        for j in adjacent_islands(h_grid, i):
            if j > i:
                idx = (i, j)
                # Variables cho 1 và 2 bridges
                x1 = idpool.id(f"x1_{idx[0]}_{idx[1]}")  # ít nhất 1 cầu 
                x2 = idpool.id(f"x2_{idx[0]}_{idx[1]}")  # chính xác 2 cầu
                x_vars[idx] = (x1, x2)
                # Ràng buộc: x2 đúng thì x1 phải đúng
                cnf.append([-x2, x1])
                # Nếu x1 sai thì x2 sai
                cnf.append([x1, -x2])

    # 2. Ràng buộc tổng số cầu của từng đảo
    for i in range(h_grid.n_islands):
        island_bridge_vars = []
        for j in adjacent_islands(h_grid, i):
            idx = (i, j) if i < j else (j, i)
            x1, x2 = x_vars[idx]
            # Thêm biến có nghĩa là >= 1 cầu (x1) và chính xác 2 cầu (x2)
            island_bridge_vars.append(x1) 
            island_bridge_vars.append(x2)  
        # Đảm bảo tổng số cầu khớp với con số trên đảo
        enc = CardEnc.equals(lits=island_bridge_vars, bound=h_grid.digits[i], encoding=1, top_id=idpool.top)
        idpool.top += 1000 
        cnf.extend(enc.clauses)

    # 3. No intersecting bridges
    for (i, j), (k, l) in combinations(x_vars.keys(), 2):
        if intersect(h_grid, i, j, k, l):
            # Ensure intersecting bridges are not both present
            cnf.append([-x_vars[(i, j)][0], -x_vars[(k, l)][0]])
                       #-x1(i,j) hoặc - x1(k,l)

    # 4. Connectivity constraint: Ensure most islands are connected
    enc = CardEnc.equals(
        lits=[x_vars[idx][0] for idx in x_vars],  # Use single bridge variables
        bound=h_grid.n_islands - 1,
        top_id=idpool.top
    )
    cnf.extend(enc.clauses)
    
    # Solve the puzzle
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print("Solution found:")
            for (i, j), (x1, x2) in x_vars.items():
                # Determine the number of bridges
                if x2 in model:
                    bridge_count = 2
                elif x1 in model:
                    bridge_count = 1
                else:
                    bridge_count = 0
                print(f"Bridge between {i} and {j}: {bridge_count}")
        else:
            print("No feasible solution found!")
            
def main():
    solve_hashi("input.txt")
            
if __name__ == "__main__":
    main()
