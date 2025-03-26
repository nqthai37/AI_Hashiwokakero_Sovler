from pysat.formula import CNF, IDPool
from pysat.solvers import Glucose4
from pysat.card import CardEnc

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

def main():
    h_grid = HashiGrid("input.txt")
    
    # Create an IDPool to automatically generate variable identifiers for PySAT
    idpool = IDPool()

    # Initialize dictionaries to hold variables
    x_vars = {}
    y_vars = {}

    # Initialize CNF formula
    cnf = CNF()
    
    for i in range(h_grid.n_islands):
        for j in range(i + 1, h_grid.n_islands):
            if j in adjacent_islands(h_grid, i):
                # Create 2 Boolean variables for log encoding of x_{ij}
                # x1 = True corresponds to x_{ij} = 1, x2 = True corresponds to x_{ij} = 2.
                x1 = idpool.id(f"x1_{i}_{j}")
                x2 = idpool.id(f"x2_{i}_{j}")
                x_vars[(i, j)] = (x1, x2)
                
                # Add clause forbidding the case (x1=True and x2=True): (¬x1 ∨ ¬x2)
                cnf.append([-x1, -x2])
                
    for i in range(h_grid.n_islands):
        adjacent_xvars = []
        for j in adjacent_islands(h_grid, i):
            # Chọn biến đã có sẵn trong `x_vars`
            idx = (i, j) if i < j else (j, i)
            x1, x2 = x_vars[idx]
            adjacent_xvars.append((x1, x2))

        # Danh sách biến để tạo ràng buộc tổng
        lits_expanded = []
        for x1, x2 in adjacent_xvars:
            lits_expanded.append(x1)
            lits_expanded.append(x2)

        # Sử dụng CardEnc thay thế PBEnc
        cnf.extend(CardEnc.equals(lits=lits_expanded, bound=h_grid.digits[i], top_id=idpool.top).clauses)
    
    
    # Check feasibility of the CNF formula
    with Glucose4(bootstrap_with=cnf.clauses) as solver:
        if solver.solve():
            print("Formula is feasible!")
            model = solver.get_model()
            print("Solution found:", model)
            
            # Decode the value of x_{ij} based on the values of x1 and x2
            for (i, j), (x1, x2) in x_vars.items():
                b1 = x1 in model  # True if x1 is assigned True
                b2 = x2 in model  # True if x2 is assigned True
                if not b1 and not b2:
                    x_val = 0
                elif b1 and not b2:
                    x_val = 1
                elif not b1 and b2:
                    x_val = 2
                else:
                    x_val = None  # Invalid case (already forbidden)
                print(f"x_{i}{j} = {x_val}")
        else:
            print("Formula is not feasible!")
            
if __name__ == "__main__":
    main()