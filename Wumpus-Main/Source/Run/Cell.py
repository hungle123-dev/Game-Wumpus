from Run.KnowledgeBase import KnowledgeBase
from Run.CellType import CellType
import utils

DDX = [(0, 1), (0, -1), (-1, 0), (1, 0)]


class Cell:
    def __init__(self, row, col, N, value):
        self.map_pos = (col + 1, N - row)
        self.matrix_pos = (row, col)
        self.index_pos = N * (col - 1) + row
        self.map_size = N

        self.explored = False
        self.percept = [False for _ in range(5)]  # [-G:0, -P:1, -W:2, -B:3, -S:4]

        self.parent = None
        self.child = []

        self.getValueInCell(value)

    def getValueInCell(self, value):
        for val in value:
            if val == CellType.GOLD.value:
                self.percept[0] = True
            elif val == CellType.PIT.value:
                self.percept[1] = True
            elif val == CellType.WUMPUS.value:
                self.percept[2] = True
            elif val == CellType.BREEZE.value:
                self.percept[3] = True
            elif val == CellType.STENCH.value:
                self.percept[4] = True
            elif val == CellType.AGENT.value or val == CellType.EMPTY.value:
                continue
            else:
                raise TypeError('Cell not valid')

    def exist_Entity(self, idx):
        return self.percept[idx]

    def check(self):
        return not self.exist_Entity(3) and not self.exist_Entity(4)

    def update_parent(self, new_parent):
        self.parent = new_parent

    def update_child(self, valid_adj_cell_list):
        adj_cell: Cell
        for adj_cell in valid_adj_cell_list:
            if adj_cell.parent is None:
                self.child.append(adj_cell)
                adj_cell.update_parent(self)

    def is_explored(self):
        return self.explored

    def explore(self):
        self.explored = True

    def grab_gold(self):
        self.percept[0] = False

    def get_adj_cell(self, cell_matrix):
        adj_cell = []
        for (d_r, d_c) in DDX:
            row = self.matrix_pos[0] + d_r
            col = self.matrix_pos[1] + d_c
            if utils.Utils.isValid(row, col, self.map_size):
                adj_cell.append(cell_matrix[row][col])

        return adj_cell

    def kill_wumpus(self, cell_matrix, kb: KnowledgeBase):
        # delete wumpus in this cell
        self.percept[2] = False

        # delete stench around this cell
        adj_cell = self.get_adj_cell(cell_matrix)
        stench_cell: Cell
        for stench_cell in adj_cell:
            flag = True
            adj_this_stench = stench_cell.get_adj_cell(cell_matrix)
            cell_wumpus: Cell
            for cell_wumpus in adj_this_stench:
                if cell_wumpus.exist_Entity(2):
                    # have wumpus
                    flag = False
                    break

            # if no another wumpus around this cell => delete stench_cell
            if flag:
                stench_cell.percept[4] = False

                # TODO: Will check again here
                # delete clause have stench
                kb.del_clause([stench_cell.get_literal(CellType.STENCH, '+')])
                # add clause dont have stench
                kb.add_clause([stench_cell.get_literal(CellType.STENCH, '-')])
                # TODO: End

                adj_cell_list = stench_cell.get_adj_cell(cell_matrix)
                # BASE KNOWLEDGE: S <=> Wa v Wb v Wc v Wd
                # (S => Wa v Wb v Wc v Wd) <=> (-S v Wa v Wb v Wc v Wd) (De Morgan)
                cell_adj: Cell
                clause = [cell_adj.get_literal(CellType.WUMPUS, '+') for cell_adj in adj_cell_list]
                clause.append(stench_cell.get_literal(CellType.STENCH, '-'))
                kb.del_clause(clause)

                # (Wa v Wb v Wc v Wd => S) <=> ((-Wa ^ -Wb ^ -Wc ^ -Wd) v S)
                for cell_adj in adj_cell_list:
                    kb.del_clause([stench_cell.get_literal(CellType.STENCH, '+'), cell_adj.get_literal(CellType.WUMPUS,
                                                                                                       '-')])

    def get_literal(self, obj: CellType, sign='+'):
        # sign='-': not operator
        if obj == CellType.PIT:
            i = 1
        elif obj == CellType.WUMPUS:
            i = 2
        elif obj == CellType.BREEZE:
            i = 3
        elif obj == CellType.STENCH:
            i = 4
        else:
            raise TypeError('Error: ' + self.get_literal.__name__)

        factor = 10 ** len(str(self.map_size * self.map_size))
        literal = i * factor + self.index_pos
        if sign == '-':
            literal *= -1

        return literal
