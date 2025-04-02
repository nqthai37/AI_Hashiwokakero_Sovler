from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4
from pysat.card import CardEnc
from itertools import combinations

from dpll import dpll_solver
from Astar import a_star_cnf
from Brute_force import brute_force_cnf 

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


def solutionToString(h_grid, bridge_count):
    empty_grid = []
    for _ in range(h_grid.n_size):
        empty_grid.append(["0"] * h_grid.n_size)  
    
    for (i,j), d in zip(h_grid.island_coords, h_grid.digits):
        empty_grid[i][j] = f"{d}"
        
    for (i,j) in bridge_count.keys():
        if bridge_count[(i,j)] > 0:
            coords_between, is_horizontal = coordinates_between(h_grid, i, j)
            for coord in coords_between:
                (x, y) = coord
                if is_horizontal:
                    empty_grid[x][y] = "-" if bridge_count[(i,j)] == 1 else "="
                else: empty_grid[x][y] = "|" if bridge_count[(i,j)] == 1 else "$"
                
    return empty_grid
        
          
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

def generate_cnf(h_grid, x_vars):
    idpool = IDPool()
    cnf = CNF()
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
    enc = CardEnc.atleast(
        lits=[x_vars[idx][0] for idx in x_vars],  # Use single bridge variables
        bound=h_grid.n_islands - 1,
        top_id=idpool.top
    )
    cnf.extend(enc.clauses)
    
    return cnf, x_vars



def solve_hashi_generic(cnf, h_grid, x_vars, solver_function):
    # Gọi hàm solver_function để giải CNF
    model = solver_function(cnf)

    if model:
        bridge_count = {}
        for (i, j), (x1, x2) in x_vars.items():
            if model.get(x2, False):
                bridge_count[(i, j)] = 2
            elif model.get(x1, False):
                bridge_count[(i, j)] = 1
            else:
                bridge_count[(i, j)] = 0

        solution = solutionToString(h_grid, bridge_count)
        return solution
    else:
        print("No feasible solution found!")
        return None

def solve_hashi_brute_force(cnf, h_grid, x_vars):
    return solve_hashi_generic(cnf, h_grid, x_vars, brute_force_cnf)

def solve_hashi_Astar(cnf, h_grid, x_vars):
    return solve_hashi_generic(cnf, h_grid, x_vars, a_star_cnf)

def solve_hashi_Backtrack(cnf, h_grid, x_vars):
    return solve_hashi_generic(cnf, h_grid, x_vars, dpll_solver)
   
def solve_hashi_Pysat(cnf, h_grid, x_vars):
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print("Solution found")
            bridge_count = {}
            for (i, j), (x1, x2) in x_vars.items():
                # Determine the number of bridges
                if x2 in model:
                    bridge_count[(i,j)] = 2
                elif x1 in model:
                    bridge_count[(i,j)] = 1
                else:
                    bridge_count[(i,j)] = 0
            solution = solutionToString(h_grid, bridge_count)
            return solution
        else:
            print("No feasible solution found!")
            return None
    
def writeFile(output, solution):
    with open(output, "w") as f:
        f.write("\n".join(" ".join(row) for row in solution))

def main():
    input = "Inputs/input-01.txt"
    num = input.split(".")[-2].split("-")[-1]
    
    h_grid = HashiGrid(input)
    x_vars = {}
    cnf, x_vars = generate_cnf(h_grid, x_vars)
    
    solution = solve_hashi_Pysat(cnf, h_grid, x_vars)
    output = "Outputs/output-" + num + ".txt"
    if solution:
        writeFile(output, solution)
            
if __name__ == "__main__":
    main()