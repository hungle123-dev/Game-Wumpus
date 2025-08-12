def standardize_clause(clause):
    return sorted(list(set(clause)))


class KnowledgeBase:
    def __init__(self):
        self.KB = []

    def add_clause(self, clause):
        clause = standardize_clause(clause)
        if clause not in self.KB:
            self.KB.append(clause)

    def del_clause(self, clause):
        clause = standardize_clause(clause)
        if clause in self.KB:
            self.KB.remove(clause)

    def infer(self, not_alpha):
        # Combine KB with negation of alpha
        all_clauses = self.KB[:]
        for clause in not_alpha:
            all_clauses.append(standardize_clause(clause))
        
        # Check if the combined set is unsatisfiable
        return not self._is_satisfiable(all_clauses)
    
    def _is_satisfiable(self, clauses):
        """
        Check if a set of clauses is satisfiable using DPLL algorithm
        """
        # Get all variables in the clauses
        variables = set()
        for clause in clauses:
            for literal in clause:
                variables.add(abs(literal))
        
        return self._dpll(clauses, list(variables), {})
    
    def _dpll(self, clauses, variables, assignment):
        """
        DPLL algorithm for SAT solving
        """
        # Simplify clauses based on current assignment
        simplified_clauses = self._simplify_clauses(clauses, assignment)
        
        # Check for contradictions (empty clause)
        for clause in simplified_clauses:
            if len(clause) == 0:
                return False
        
        # Remove satisfied clauses
        simplified_clauses = [clause for clause in simplified_clauses if len(clause) > 0]
        
        # If no clauses left, we have a satisfying assignment
        if len(simplified_clauses) == 0:
            return True
        
        # Unit propagation
        while True:
            unit_clause = None
            for clause in simplified_clauses:
                if len(clause) == 1:
                    unit_clause = clause[0]
                    break
            
            if unit_clause is None:
                break
            
            # Assign the unit literal
            var = abs(unit_clause)
            value = unit_clause > 0
            assignment[var] = value
            
            # Simplify clauses again
            simplified_clauses = self._simplify_clauses(simplified_clauses, assignment)
            
            # Check for contradictions
            for clause in simplified_clauses:
                if len(clause) == 0:
                    return False
            
            # Remove satisfied clauses
            simplified_clauses = [clause for clause in simplified_clauses if len(clause) > 0]
        
        # If no clauses left after unit propagation
        if len(simplified_clauses) == 0:
            return True
        
        # Choose a variable to branch on
        if len(variables) == 0:
            return True
        
        # Find an unassigned variable
        unassigned_var = None
        for var in variables:
            if var not in assignment:
                unassigned_var = var
                break
        
        if unassigned_var is None:
            return True
        
        # Try both values for the chosen variable
        # Try True first
        new_assignment = assignment.copy()
        new_assignment[unassigned_var] = True
        if self._dpll(simplified_clauses, variables, new_assignment):
            return True
        
        # Try False
        new_assignment = assignment.copy()
        new_assignment[unassigned_var] = False
        if self._dpll(simplified_clauses, variables, new_assignment):
            return True
        
        return False
    
    def _simplify_clauses(self, clauses, assignment):
        """
        Simplify clauses based on current variable assignment
        """
        simplified = []
        
        for clause in clauses:
            new_clause = []
            satisfied = False
            
            for literal in clause:
                var = abs(literal)
                if var in assignment:
                    # Variable is assigned
                    if (literal > 0 and assignment[var]) or (literal < 0 and not assignment[var]):
                        # Literal is satisfied, entire clause is satisfied
                        satisfied = True
                        break
                    # else: literal is false, don't add to new clause
                else:
                    # Variable not assigned yet, keep literal
                    new_clause.append(literal)
            
            if not satisfied:
                simplified.append(new_clause)
        
        return simplified
