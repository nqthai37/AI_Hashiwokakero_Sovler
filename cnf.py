#dk 1: moi canh chi co toi da 2 cay cau
# -Xij1 V -Xij2
cnf.append([-x_ij_1, -x_ij_2])
#dk 2: tong cau va so tren dao phai bang nhau 
# tren dao i ghi so cau la k thi: 
# (x_ij_1 + x_ij_2 + ... + x_ij_k) = k
for i in range(n_islands):
    clauses = [] # danh sach cac menh de hop le cho dao i
    adjacent = adjacent_islands(i)
    
    for values in range(h_grid.digits[i] + 1):  
        clause = []
        for j in adjacent:
            clause.append(x_vars[(i, j)][0])  # x_ij_1
            clause.append(2 * x_vars[(i, j)][1])  # x_ij_2
        if sum(clause) == h_grid.digits[i]: # neu tong cau bang so cau quy dinh thi add vao clauses
            clauses.append(clause)
    
    cnf.extend(clauses) 
# dk3: tranh cau cat nhau
# Yij la cau noi tu i den j, =0 khi khong co cau noi, =1 khi co cau noi
# -Yij V -Yqp neu 2 cau cat nhau thi hoac bo cau ij hoac bo cau qp
for i, a in enumerate(y_vars):   # lay cau a=[i1, i2]
    for b in list(y_vars.keys())[i + 1 :]:  # lay cau b=[j1, j2] xet dieu kien sau a de ko bi trung lap
        if intersect(h_grid, a[0], a[1], b[0], b[1]): # xet xem 2 cau co giao nhau hay ko  
            model.Add(y_vars[a] + y_vars[b] <= 1)  # neu giao nhau thi bo 1 cau 
            
#dk 4: dam bao cac dao lien thong voi nhau
# do thi lien thong n dinh co it nhat n-1 canh, neu it hon se co chu trinh con bi tach biet
# y_vars.values() la tong cac cau noi giua cac dao (cau kep cung duoc tinh la 1 o bien nay)
model.Add(sum(y_vars.values()) >= h_grid.n_islands - 1)


