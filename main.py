
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
    min_dis = {1000000, 1000000, 1000000, 1000000}
    # top, left , bottom , right
    min_idx = {-1, -1, -1, -1}    

    for i in range(len(h_grid.island_coords)):
            x1,y1 = h_grid.island_coords[i]
            #find top neighbor
            if x1 == x and y1 < y:
                sub_min = abs(y1-y)
                if sub_min < min_dis[0]:
                    min_dis[0] = sub_min
                    min_idx[0] = i
            #find left neighbor
            if y1 == y and x1 < x:
                sub_min = abs(x1-x)
                if sub_min < min_dis[1]:
                    min_dis[1] = sub_min
                    min_idx[1] = i
            #find bottom neighbor
            if x1 == x and y1 > y:
                sub_min = abs(y1-y)
                if sub_min < min_dis[2]:
                    min_dis[2] = sub_min
                    min_idx[2] = i
            #find right neighbor
            if y1 == y and x1 > x:
                sub_min = abs(y1-y)
                if sub_min < min_dis[3]:
                    min_dis[3] = sub_min
                    min_idx[3] = i
    for idx in min_idx:
        if (idx != -1):
            adj_islands.append(idx)

    return adj_islands
