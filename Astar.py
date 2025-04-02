import heapq


def heuristic(cnf, assignment):
    """Tính toán số điều khoản chưa được thỏa mãn."""
    unsatisfied = 0
    for clause in cnf.clauses:
        if not any((lit > 0 and assignment.get(abs(lit), False)) or
                   (lit < 0 and not assignment.get(abs(lit), False))
                   for lit in clause):
            unsatisfied += 1
    return unsatisfied

def a_star_cnf(cnf):
    """Giải CNF sử dụng A*."""
    all_vars = set(abs(lit) for clause in cnf.clauses for lit in clause)
    
    # Khởi tạo hàng đợi ưu tiên
    frontier = []
    heapq.heappush(frontier, (0, tuple(), 0))  # (f(n), assignment (as tuple), num_satisfied)
    
    while frontier:
        _, assignment_tuple, num_satisfied = heapq.heappop(frontier)
        assignment = dict(assignment_tuple)  # Chuyển tuple thành dict
        
        # Kiểm tra nếu đã thỏa mãn tất cả điều khoản
        if num_satisfied == len(cnf.clauses):
            return assignment
        
        # Tìm biến chưa được gán
        unassigned = next((v for v in all_vars if v not in assignment), None)
        if unassigned is None:
            continue
        
        for value in [False, True]:
            new_assignment = assignment.copy()
            new_assignment[unassigned] = value
            
            new_satisfied = sum(1 for clause in cnf.clauses if any(
                (lit > 0 and new_assignment.get(abs(lit), False)) or
                (lit < 0 and not new_assignment.get(abs(lit), False))
                for lit in clause
            ))
            h_value = heuristic(cnf, new_assignment)
            f_value = new_satisfied + h_value
            heapq.heappush(frontier, (f_value, tuple(sorted(new_assignment.items())), new_satisfied))
    
    return None  # Không tìm thấy lời giải