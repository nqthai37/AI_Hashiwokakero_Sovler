from utility_function import unit_propagation, pure_literal_elimination

def dpll_cnf(cnf):
    # Step 1: Collect and sort variables by frequency (heuristic)
    variables = sorted(
        {abs(lit) for clause in cnf.clauses for lit in clause},
        key=lambda v: -sum(1 for clause in cnf.clauses for lit in clause if abs(lit) == v)
    )

    # Initialize assignment (0 = unassigned, 1 = True, -1 = False)
    assignment = {var: 0 for var in variables}
    
    def dpll(assignment, depth=0):
        # Apply pure literal elimination
        assignment = pure_literal_elimination(assignment.copy(), cnf)
        
        # Apply unit propagation
        if not unit_propagation(assignment, cnf):
            return None  # Conflict
        
        # Check if all clauses are satisfied
        if all(
            any((lit > 0 and assignment[abs(lit)] == 1) or 
                (lit < 0 and assignment[abs(lit)] == -1) 
                for lit in clause)
            for clause in cnf.clauses
        ):
            return assignment
        
        # Select next unassigned variable
        for var in variables:
            if assignment[var] == 0:
                break
        else:
            return None  # No unassigned vars but not all clauses satisfied (shouldn't happen)
        
        # Try assigning True
        new_assignment = assignment.copy()
        new_assignment[var] = 1
        result = dpll(new_assignment, depth + 1)
        if result is not None:
            return result
        
        # Try assigning False
        new_assignment = assignment.copy()
        new_assignment[var] = -1
        return dpll(new_assignment, depth + 1)

    return dpll(assignment) 