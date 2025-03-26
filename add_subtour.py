def add_subtour_elimination(model, subtour_islands, y_vars):
	"""Adds a subtour elimination constraint"""
	exiting_bridges = []
	for (from_island, to_island), y in y_vars.items():
		if (from_island in subtour_islands) != (to_island in subtour_islands):
			exiting_bridges.append(y)
	model.Add(sum(exiting_bridges) >= 1)

def write_solution(grid_name: str, solution: str):
    # neu chua co thu muc solutions thi tao
    if not os.path.exists("solutions"): 
        os.mkdir("solutions")
    # tao duong da dan den file luu ket qua
    file = os.path.join("solutions", grid_name)
    with open(file, "a+") as f:
        f.write(solution + "\n\n")