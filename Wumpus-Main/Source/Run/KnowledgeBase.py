from pysat.solvers import Glucose3


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
        g = Glucose3()
        for clause in self.KB:
            g.add_clause(clause)
        for clause in not_alpha:
            g.add_clause(clause)

        return not g.solve()
