import heapq

class AStarNode:
    def __init__(self, f_value, g_value, current_assignment):
        self.f_value = f_value
        self.g_value = g_value
        self.current_assignment = current_assignment

    def __lt__(self, other):
        # So sánh dựa trên f_value (dùng để sắp xếp trong heap)
        return self.f_value < other.f_value

    def __eq__(self, other):
        # So sánh nếu hai node có cùng f_value và current_assignment
        return (self.f_value == other.f_value and
                self.g_value == other.g_value and
                self.current_assignment == other.current_assignment)

    def __repr__(self):
        return f"AStarNode(f={self.f_value}, g={self.g_value}, assignment={self.current_assignment})"

def a_star_cnf(cnf):
    variables = sorted(
        {abs(lit) for clause in cnf.clauses for lit in clause},
        key=lambda v: -sum(1 for clause in cnf.clauses for lit in clause if abs(lit) == v)
    )

    assignment = {var: 0 for var in variables}

    def unit_propagation(assignment):
        changed = True
        while changed:
            changed = False
            for clause in cnf.clauses:
                unassigned = []
                satisfied = False
                for lit in clause:
                    var = abs(lit)
                    if assignment[var] != 0:
                        if (lit > 0 and assignment[var] == 1) or (lit < 0 and assignment[var] == -1):
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)

                if satisfied:
                    continue
                if not unassigned:
                    return False  # Conflict
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    var = abs(lit)
                    new_val = 1 if lit > 0 else -1
                    if assignment[var] == 0:
                        assignment[var] = new_val
                        changed = True
                    elif assignment[var] != new_val:
                        return False
        return True

    def pure_literal_elimination(assignment):
        literal_sign = {}
        for clause in cnf.clauses:
            for lit in clause:
                var = abs(lit)
                if var in literal_sign:
                    if literal_sign[var] != (lit > 0):
                        literal_sign[var] = None  # Not pure
                else:
                    literal_sign[var] = (lit > 0)

        for var, sign in literal_sign.items():
            if sign is not None and assignment[var] == 0:
                assignment[var] = 1 if sign else -1
        return assignment

    def heuristic(assignment):
        unsatisfied = 0
        for clause in cnf.clauses:
            if not any((lit > 0 and assignment[abs(lit)] == 1) or 
                       (lit < 0 and assignment[abs(lit)] == -1) 
                       for lit in clause):
                unsatisfied += 1
        return unsatisfied
        

    def a_star():
        # Initialize the priority queue (open list)
        open_list = []
        initial_node = AStarNode(0 + heuristic(assignment), 0, assignment)
        heapq.heappush(open_list, initial_node)
        closed_list = set()

        while open_list:
            current_node = heapq.heappop(open_list)

            # Apply unit propagation
            if not unit_propagation(current_node.current_assignment):
                continue  # Conflict, skip

            # Apply pure literal elimination
            current_assignment = pure_literal_elimination(current_node.current_assignment)

            # Check if all clauses are satisfied
            if all(
                any((lit > 0 and current_assignment[abs(lit)] == 1) or 
                    (lit < 0 and current_assignment[abs(lit)] == -1) 
                    for lit in clause)
                for clause in cnf.clauses
            ):
                return current_assignment  # Found a solution

            # Find the next unassigned variable
            for var in variables:
                if current_assignment[var] == 0:
                    break
            else:
                continue  # No unassigned variables, continue

            # Try assigning True
            new_assignment_true = current_assignment.copy()
            new_assignment_true[var] = 1
            f_true = heuristic(new_assignment_true)
            if tuple(new_assignment_true.items()) not in closed_list:
                new_node_true = AStarNode(f_true, current_node.g_value + 1, new_assignment_true)
                heapq.heappush(open_list, new_node_true)
                closed_list.add(tuple(new_assignment_true.items()))

            # Try assigning False
            new_assignment_false = current_assignment.copy()
            new_assignment_false[var] = -1
            f_false = heuristic(new_assignment_false)
            if tuple(new_assignment_false.items()) not in closed_list:
                new_node_false = AStarNode(f_false, current_node.g_value + 1, new_assignment_false)
                heapq.heappush(open_list, new_node_false)
                closed_list.add(tuple(new_assignment_false.items()))

        return None  # No solution found

    return a_star()  # Run the A* search algorithm