from itertools import product
from utility_function import unit_propagation, pure_literal_elimination

def brute_force_cnf(cnf):
    # Step 1: Collect all variables (positive and negative literals)
    variables = sorted({abs(lit) for clause in cnf.clauses for lit in clause})


    # Step 2: Generate all possible assignments for the variables
    all_assignments = product([1, -1], repeat=len(variables))

    # Step 3: Try each assignment and apply heuristics (Unit Propagation and Pure Literal Elimination)
    for assignment_tuple in all_assignments:
        assignment = {var: 0 for var in variables}
        
        # Convert the tuple to an assignment dictionary
        for i, var in enumerate(variables):
            assignment[var] = assignment_tuple[i]
        
        # Apply unit propagation
        if not unit_propagation(assignment.copy(), cnf):
            continue  # Conflict, skip this assignment
        
        # Apply pure literal elimination
        assignment = pure_literal_elimination(assignment, cnf)

        # Step 4: Check if all clauses are satisfied
        if all(
            any((lit > 0 and assignment[abs(lit)] == 1) or 
                (lit < 0 and assignment[abs(lit)] == -1) 
                for lit in clause)
            for clause in cnf.clauses
        ):
            return assignment  # Found a solution

    return None  # No solution found