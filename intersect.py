def intersect(a_h, b_h, coords_a, coords_b, coord_to_var):
    cnf = []
    #2 cay cau co huong khac nhau (XOR)
    #(a_h or b_h) va (not a_h or not b_h)
    cnf.append([a_h, b_h])
    cnf.append([-a_h, -b_h])

    #2 cay cau co it nhat 1 toa do chung
    common_coords = set(coords_a).intersection(coords_b)
    if not common_coords:
        cnf.append([])
        return cnf, None
    
    #I bieu dien giao nhau
    max_var = max(list(coord_to_var.values()) + [a_h, b_h])
    I = max_var + 1

    #menh de: -c v I
    for c in common_coords:
        cnf.append([-coord_to_var[c], I])

    #neu I sai thi khong co toa do chung
    clause = [-I] + [coord_to_var[c] for c in common_coords]
    cnf.append(clause)

    #buoc xay ra giao nhau
    cnf.append([I])

    return cnf, I