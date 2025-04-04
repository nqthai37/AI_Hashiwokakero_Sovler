def unit_propagation(assignment, cnf):
        """forces unit clauses and detects conflicts."""
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

def pure_literal_elimination(assignment, cnf):
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