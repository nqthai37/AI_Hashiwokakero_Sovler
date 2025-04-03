from itertools import product

def brute_force_cnf(cnf):
    # Step 1: Collect all variables (positive and negative literals)
    variables = sorted({abs(lit) for clause in cnf.clauses for lit in clause})

    def unit_propagation(assignment):
        """Applies unit propagation."""
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
        """Assign pure literals."""
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

    # Step 2: Generate all possible assignments for the variables
    all_assignments = product([1, -1], repeat=len(variables))

    # Step 3: Try each assignment and apply heuristics (Unit Propagation and Pure Literal Elimination)
    for assignment_tuple in all_assignments:
        assignment = {var: 0 for var in variables}
        
        # Convert the tuple to an assignment dictionary
        for i, var in enumerate(variables):
            assignment[var] = assignment_tuple[i]
        
        # Apply unit propagation
        if not unit_propagation(assignment.copy()):
            continue  # Conflict, skip this assignment
        
        # Apply pure literal elimination
        assignment = pure_literal_elimination(assignment)

        # Step 4: Check if all clauses are satisfied
        if all(
            any((lit > 0 and assignment[abs(lit)] == 1) or 
                (lit < 0 and assignment[abs(lit)] == -1) 
                for lit in clause)
            for clause in cnf.clauses
        ):
            return assignment  # Found a solution

    return None  # No solution found