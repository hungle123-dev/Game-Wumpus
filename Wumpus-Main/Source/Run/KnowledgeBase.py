def standardize_clause(clause):
    return sorted(list(set(clause)))


class KnowledgeBase:
    def __init__(self):
        self.KB = []  # Clauses in CNF
        self.facts = set()  # Known facts (positive literals)
        self.rules = []  # Horn clauses for forward chaining

    def add_clause(self, clause):
        """Add a clause to the knowledge base"""
        clause = standardize_clause(clause)
        if clause not in self.KB:
            self.KB.append(clause)
            
            # If it's a unit clause (fact), add to facts
            if len(clause) == 1:
                literal = clause[0]
                if literal > 0:  # Positive literal
                    self.facts.add(literal)
                    
            # Convert to Horn clause if possible for forward chaining
            self._convert_to_horn_clause(clause)

    def del_clause(self, clause):
        clause = standardize_clause(clause)
        if clause in self.KB:
            self.KB.remove(clause)

    def _convert_to_horn_clause(self, clause):
        """Convert clause to Horn clause format for forward chaining"""
        # Horn clause: at most one positive literal
        positive_literals = [lit for lit in clause if lit > 0]
        negative_literals = [abs(lit) for lit in clause if lit < 0]
        
        if len(positive_literals) <= 1:
            # Valid Horn clause
            if len(positive_literals) == 1:
                # Rule: negative_literals -> positive_literal
                conclusion = positive_literals[0]
                premises = negative_literals
                self.rules.append((premises, conclusion))
            else:
                # Constraint: all negative literals cannot be true together
                # This is handled differently in forward chaining
                pass

    def infer(self, not_alpha):
        """
        Use forward chaining to check if alpha can be inferred
        not_alpha is the negation of what we want to prove
        If KB ∪ ¬α is unsatisfiable, then KB ⊨ α
        """
        # For forward chaining, we'll use a different approach
        # We'll check if we can derive the positive form of not_alpha
        
        if len(not_alpha) == 1 and len(not_alpha[0]) == 1:
            target_literal = not_alpha[0][0]
            if target_literal < 0:
                # We want to prove the positive form
                target_fact = abs(target_literal)
                return self._forward_chaining(target_fact)
        
        # Fallback to basic logic for complex queries
        return False
    
    def _forward_chaining(self, target_fact):
        """
        Forward chaining algorithm to derive target_fact
        """
        # Start with known facts
        derived_facts = self.facts.copy()
        new_facts_added = True
        
        while new_facts_added:
            new_facts_added = False
            
            # Check each rule
            for premises, conclusion in self.rules:
                # If conclusion already derived, skip
                if conclusion in derived_facts:
                    continue
                    
                # Check if all premises are satisfied
                all_premises_satisfied = True
                for premise in premises:
                    if premise not in derived_facts:
                        all_premises_satisfied = False
                        break
                
                # If all premises satisfied, derive conclusion
                if all_premises_satisfied:
                    derived_facts.add(conclusion)
                    new_facts_added = True
                    
                    # If we derived our target, return True
                    if conclusion == target_fact:
                        return True
        
        # Check if target fact was derived
        return target_fact in derived_facts
    
    def get_derived_facts(self):
        """Get all facts that can be derived using forward chaining"""
        derived_facts = self.facts.copy()
        new_facts_added = True
        
        while new_facts_added:
            new_facts_added = False
            
            for premises, conclusion in self.rules:
                if conclusion in derived_facts:
                    continue
                    
                all_premises_satisfied = True
                for premise in premises:
                    if premise not in derived_facts:
                        all_premises_satisfied = False
                        break
                
                if all_premises_satisfied:
                    derived_facts.add(conclusion)
                    new_facts_added = True
        
        return derived_facts

    def model_count(self):
        """
        Compatibility method for legacy calls
        Returns number of known facts for Forward Chaining
        """
        return len(self.facts)

    def add_fact(self, fact):
        """Add a fact (positive literal) directly"""
        if isinstance(fact, int) and fact > 0:
            self.facts.add(fact)
            
    def add_rule(self, premises, conclusion):
        """Add a rule directly: premises -> conclusion"""
        self.rules.append((premises, conclusion))
