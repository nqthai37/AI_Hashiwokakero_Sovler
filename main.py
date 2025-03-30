from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4
from pysat.card import CardEnc
from itertools import combinations
import time

# Then use your original recursive solver

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
    
    min_dis = [float('inf')] * 4  # top, left, bottom, right
    min_idx = [-1, -1, -1, -1]    

    for i in range(len(h_grid.island_coords)):
        x1, y1 = h_grid.island_coords[i]
        # find top neighbor
        if x1 < x and y1 == y:
            sub_min = abs(x1 - x)
            if sub_min < min_dis[0]:
                min_dis[0] = sub_min
                min_idx[0] = i
        # find left neighbor
        elif y1 < y and x1 == x:
            sub_min = abs(y1 - y)
            if sub_min < min_dis[1]:
                min_dis[1] = sub_min
                min_idx[1] = i
        # find bottom neighbor
        elif x1 > x and y1 == y:
            sub_min = abs(x1 - x)
            if sub_min < min_dis[2]:
                min_dis[2] = sub_min
                min_idx[2] = i
        # find right neighbor
        elif y1 > y and x1 == x:
            sub_min = abs(y1 - y)
            if sub_min < min_dis[3]:
                min_dis[3] = sub_min
                min_idx[3] = i
                
    for idx in min_idx:
        if idx != -1:
            adj_islands.append(idx)
    
    return adj_islands            

def coordinates_between(h_grid, i, j):
    coordinates = [] 
    is_horizontal = None 
    
    # horizontal bridge
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
    # vertical bridge
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
    coords_a, bridge_a_vertical = coordinates_between(h_grid, ai, aj)
    coords_b, bridge_b_vertical = coordinates_between(h_grid, bi, bj)

    if not coords_a or not coords_b:
        return False
    if bridge_a_vertical != bridge_b_vertical:
        return bool(set(coords_a) & set(coords_b))
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
                # Variables for 0, 1, or 2 bridges
                x0 = idpool.id(f"x0_{i}_{j}")  # no bridge
                x1 = idpool.id(f"x1_{i}_{j}")  # single bridge
                x2 = idpool.id(f"x2_{i}_{j}")  # double bridge
                x_vars[idx] = (x0, x1, x2)
                
                # Exactly one of these must be true
                cnf.append([x0, x1, x2])
                cnf.append([-x0, -x1])
                cnf.append([-x0, -x2])
                cnf.append([-x1, -x2])

    # 2. Sum constraints for each island
    for i in range(h_grid.n_islands):
        bridge_vars = []
        # For single bridges (count as 1)
        for j in adjacent_islands(h_grid, i):
            idx = (i, j) if i < j else (j, i)
            x0, x1, x2 = x_vars[idx]
            bridge_vars.append(x1)
        
        # For double bridges (need to count as 2)
        # We represent this by adding the variable twice
        for j in adjacent_islands(h_grid, i):
            idx = (i, j) if i < j else (j, i)
            x0, x1, x2 = x_vars[idx]
            bridge_vars.append(x2)
            bridge_vars.append(x2)  # add twice to count as 2
        
        # Create cardinality constraint for exact sum
        enc = CardEnc.equals(lits=bridge_vars, bound=h_grid.digits[i], top_id=idpool.top)
        cnf.extend(enc.clauses)
        idpool.top = enc.nv + 1

    # 3. No intersecting bridges
    for (i, j), (k, l) in combinations(x_vars.keys(), 2):
        if intersect(h_grid, i, j, k, l):
            # At most one of these bridges can exist
            x0_i, x1_i, x2_i = x_vars[(i,j)]
            x0_k, x1_k, x2_k = x_vars[(k,l)]
            cnf.append([-x1_i, -x1_k])
            cnf.append([-x1_i, -x2_k])
            cnf.append([-x2_i, -x1_k])
            cnf.append([-x2_i, -x2_k])

    return cnf, x_vars, h_grid

def pySat_solver(cnf, x_vars,h_grid):

    # Solve the puzzle
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print("\nSolution found:")
            
            # Collect all bridges for visualization
            bridges = []
            for (i, j), (x0, x1, x2) in x_vars.items():
                if x1 in model and x1 > 0:
                    bridges.append((i, j, 1))
                elif x2 in model and x2 > 0:
                    bridges.append((i, j, 2))
            
            # Print solution with coordinates
            for bridge in bridges:
                i, j, count = bridge
                coord1 = h_grid.island_coords[i]
                coord2 = h_grid.island_coords[j]
                print(f"Bridge between {coord1} and {coord2}: {count} bridge{'s' if count > 1 else ''}")
            
            # Verify connectivity (basic check)
            if len(bridges) >= h_grid.n_islands - 1:
                print("\nGraph appears to be connected.")
            else:
                print("\nWarning: Graph may not be fully connected.")
        else:
            print("No feasible solution found!")

def backtracking_solver(cnf):
    # Đếm tần suất biến và sắp xếp
    variable_counts = {}
    for clause in cnf.clauses:
        for lit in clause:
            var = abs(lit)
            variable_counts[var] = variable_counts.get(var, 0) + 1
    variables = sorted(variable_counts.keys(), key=lambda v: -variable_counts[v])

    # Khởi tạo assignment
    assignment = {var: 0 for var in variables}

    def unit_propagation(assignment):
        """Tương tự như phiên bản trước"""
        changed = True
        while changed:
            changed = False
            for clause in cnf.clauses:
                satisfied = False
                unassigned_lits = []
                
                for lit in clause:
                    var = abs(lit)
                    if assignment[var] != 0:
                        if (lit > 0 and assignment[var] == 1) or (lit < 0 and assignment[var] == -1):
                            satisfied = True
                            break
                    else:
                        unassigned_lits.append(lit)
                
                if satisfied:
                    continue
                
                if not unassigned_lits:
                    return False
                
                if len(unassigned_lits) == 1:
                    lit = unassigned_lits[0]
                    var = abs(lit)
                    new_value = 1 if lit > 0 else -1
                    
                    if assignment[var] == 0:
                        assignment[var] = new_value
                        changed = True
                    elif assignment[var] != new_value:
                        return False
        return True

    def backtrack(assignment, index):
        # Base case: đã gán hết tất cả biến
        if index == len(variables):
            # Kiểm tra tất cả mệnh đề đều thỏa mãn
            for clause in cnf.clauses:
                if not any((lit > 0 and assignment[abs(lit)] == 1) or 
                   (lit < 0 and assignment[abs(lit)] == -1) for lit in clause):
                    return None
            return assignment
        
        var = variables[index]
        
        # Thử gán giá trị False trước
        for value in [-1, 1]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            
            # Áp dụng unit propagation
            if not unit_propagation(new_assignment):
                continue
            
            # Đệ quy
            result = backtrack(new_assignment, index + 1)
            if result is not None:
                return result
        
        return None

    return backtrack(assignment, 0)

def backtrack_solver(cnf, x_vars, h_grid):
    solution = backtracking_solver(cnf)

    if solution:
        print("\nSolution found:")
        bridges = [
            (i, j, 1) if solution.get(x1, 0) == 1 else (i, j, 2)
            for (i, j), (x0, x1, x2) in x_vars.items()
            if solution.get(x1, 0) == 1 or solution.get(x2, 0) == 1
        ]

        for i, j, count in bridges:
            coord1, coord2 = h_grid.island_coords[i], h_grid.island_coords[j]
            print(f"Bridge between {coord1} and {coord2}: {count} bridge{'s' if count > 1 else ''}")
    else:
        print("No feasible solution found!")

    
def main():
    cnf, x_vars, h_grid = solve_hashi("input.txt")
    print("Solving with PySAT...")
    start = time.time()
    pySat_solver(cnf, x_vars, h_grid)
    end = time.time()
    print(f"Time taken: {end - start:.4f} seconds")
    print("\nSolving with Backtracking...")
    start = time.time()
    backtrack_solver(cnf, x_vars, h_grid)
    end = time.time()
    print(f"Time taken: {end - start:.4f} seconds")
    print("\nDone!")
    
            
if __name__ == "__main__":
    main()