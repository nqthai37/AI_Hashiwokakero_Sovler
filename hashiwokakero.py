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

    def printGrid(self):
        for i in range(len(self.island_coords)):
            print(f'Island {self.island_coords[i]} with bridges = {self.digits[i]}')


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

def intersect(h_grid, ai, aj, bi, bj):
    coords_under_a, bridge_a_vertical = coordinates_between(h_grid, ai, aj)
    coords_under_b, bridge_b_vertical = coordinates_between(h_grid, bi, bj)

    if bridge_a_vertical != bridge_b_vertical:
        return bool(set(coords_under_a) & set(coords_under_b))
    return False

def coordinates_between(h_grid, i, j):
	# ham nay co nhiem vu tao va ghi lai toa do cua cau, th1 laf cau ngang = true, th2 la cau doc = false, neu k tim thay la cau cheo = None 
	coordinates = [] # khoi tao list rong de chua toa do cua cau
	is_horizontal = None # dau tien khoi tao k co cau
	
	# xet cau ngang
	if h_grid.island_coords[i][0] == h_grid.island_coords[j][0]: # lay toa do x ra so, neu bang thi nam ngang
		x = h_grid.island_coords[i][0]
		coordinates = [
			(x, y)
			for y in range(
				h_grid.island_coords[i][1] + 1, h_grid.island_coords[j][1]
			)
		]
		is_horizontal = True
	# xet cau doc
	elif h_grid.island_coords[i][1] == h_grid.island_coords[j][1]: #lay toa do cua y so sanh, neu bang thi doc
		y = h_grid.island_coords[i][1]
		coordinates = [
			(x, y)
			for x in range(
				h_grid.island_coords[i][0] + 1, h_grid.island_coords[j][0]
			)
		]
		is_horizontal = False
	return coordinates, is_horizontal # tra ve toa do va kieu cua cau

# def find_subtour(h_grid, solver, y_vars):
#     bridges = {island: [] for island in range(h_grid.n_islands)}
#     for bridge, var in y_vars.items():
#         if solver.Value(var):
#             i, j = bridge
#             if i not in bridges:
#                 bridges[i] = []
#             if j not in bridges:
#                 bridges[j] = []
#             bridges[i].append(j)
#             bridges[j].append(i)

#     subtour_islands = {0}

#     def scan(island):
#         while bridges[island]:
#             successor = bridges[island].pop(0)
#             bridges[successor].remove(island)
#             if successor not in subtour_islands:
#                 subtour_islands.add(successor)
#                 scan(successor)

#     scan(0)
    
#     if len(subtour_islands) != h_grid.n_islands:
#         return subtour_islands
#     return None

def solve_hashi(filename):
    h_grid = HashiGrid(filename)
    idpool = IDPool()
    cnf = CNF()
    x_vars, y_vars = {}, {}

    for i in range(h_grid.n_islands):
        for j in adjacent_islands(h_grid, i):
            idx = (min(i, j), max(i, j))
            x1, x2 = idpool.id(f"x1_{idx[0]}_{idx[1]}"), idpool.id(f"x2_{idx[0]}_{idx[1]}")
            y = idpool.id(f"y_{idx[0]}_{idx[1]}")
            x_vars[idx], y_vars[idx] = (x1, x2), y
            cnf.append([-x1, -x2])  # Ensure x1 and x2 are not both True
            cnf.append([-y, x1, x2])  # If y = 1, then x1 or x2 must be 1
            cnf.append([-x1, y])
            cnf.append([-x2, y])

    for i in range(h_grid.n_islands):
        adjacent_xvars = [x_vars[(min(i, j), max(i, j))] for j in adjacent_islands(h_grid, i)]
        cnf.extend(CardEnc.equals(
            lits=[x for pair in adjacent_xvars for x in pair],
            bound=h_grid.digits[i],
            top_id=idpool.top
        ).clauses)

    for (i, j), (k, l) in combinations(y_vars.keys(), 2):
        if intersect(h_grid, i, j, k, l):
            cnf.append([-y_vars[(i, j)], -y_vars[(k, l)]])

    cnf.extend(CardEnc.atleast(
        lits=list(y_vars.values()),
        bound=h_grid.n_islands - 1,
        top_id=idpool.top
    ).clauses)

    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print("Solution found:")
            for (i, j), (x1, x2) in x_vars.items():
                b1, b2 = x1 in model, x2 in model
                x_val = 0 if not b1 and not b2 else (1 if b1 and not b2 else 2)
                print(f"x_{i}{j} = {x_val}")
        else:
            print("No feasible solution found!")
            
def main():
    solve_hashi("input.txt")
            
if __name__ == "__main__":
    main()