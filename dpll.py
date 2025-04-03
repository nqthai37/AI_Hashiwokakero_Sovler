def dpll_cnf(cnf):
    # Step 1: Collect and sort variables by frequency (heuristic)
    variables = sorted(
        {abs(lit) for clause in cnf.clauses for lit in clause},
        key=lambda v: -sum(1 for clause in cnf.clauses for lit in clause if abs(lit) == v)
    )

    # Initialize assignment (0 = unassigned, 1 = True, -1 = False)
    assignment = {var: 0 for var in variables}

    def unit_propagation(assignment):
        """Same as before, forces unit clauses and detects conflicts."""
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
        """Assign pure literals (those appearing only positively/negatively)."""
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

    def dpll(assignment, depth=0):
        # Apply pure literal elimination
        assignment = pure_literal_elimination(assignment.copy())
        
        # Apply unit propagation
        if not unit_propagation(assignment):
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