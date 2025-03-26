def coordinates_between(h_grid, i, j):
	# ham nay co nhiem vu tao va ghi lai toa do cua cau, th1 laf cau ngang = true, th2 la cau doc = false, neu k tim thay la cau cheo = None 
	coordinates = [] # khoi tao list rong de chua toa do cua cau
	is_horizontal = None # dau tien khoi tao k co cau
	
	# xet cau ngang
	if h_grid.island_coordinates[i][0] == h_grid.island_coordinates[j][0]: # lay toa do x ra so, neu bang thi nam ngang
		x = h_grid.island_coordinates[i][0]
		coordinates = [
			(x, y)
			for y in range(
				h_grid.island_coordinates[i][1] + 1, h_grid.island_coordinates[j][1]
			)
		]
		is_horizontal = True
	# xet cau doc
	elif h_grid.island_coordinates[i][1] == h_grid.island_coordinates[j][1]: #lay toa do cua y so sanh, neu bang thi doc
		y = h_grid.island_coordinates[i][1]
		coordinates = [
			(x, y)
			for x in range(
				h_grid.island_coordinates[i][0] + 1, h_grid.island_coordinates[j][0]
			)
		]
		is_horizontal = False
	return coordinates, is_horizontal # tra ve toa do va kieu cua cau