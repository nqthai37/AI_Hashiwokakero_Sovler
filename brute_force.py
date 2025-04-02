from itertools import product

def brute_force_cnf(cnf):
    # Lấy tất cả các biến xuất hiện trong CNF
    all_vars = set(abs(lit) for clause in cnf.clauses for lit in clause)
    n = len(all_vars)  # Số lượng biến cần duyệt

    # Sắp xếp danh sách biến để duyệt theo thứ tự
    var_list = sorted(all_vars)

    # Duyệt tất cả các tổ hợp gán giá trị cho biến
    for assignment in product([False, True], repeat=n):
        model = {var_list[i]: assignment[i] for i in range(n)}

        # Kiểm tra xem mô hình này có thỏa mãn tất cả các mệnh đề CNF không
        satisfied = True
        for clause in cnf.clauses:
            clause_satisfied = False
            for literal in clause:
                var = abs(literal)  # Lấy biến từ literal
                value = model[var]  # Lấy giá trị True/False của biến

                # Nếu biến dương (literal > 0) thì cần giá trị True
                # Nếu biến âm (literal < 0) thì cần giá trị False
                if (literal > 0 and value) or (literal < 0 and not value):
                    clause_satisfied = True
                    break  # Mệnh đề này thỏa mãn, không cần kiểm tra tiếp

            if not clause_satisfied:
                satisfied = False
                break  # CNF không thỏa mãn, thử tổ hợp tiếp theo
        
        if satisfied:
            return model  # Trả về lời giải hợp lệ

    return None  # Trả về None nếu không có lời giải hợp lệ