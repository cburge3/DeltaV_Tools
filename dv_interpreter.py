# takes an expression tree object and interprets it into human readable expressions
# this particular implementation is for a 3M interlock documentation program

from dv_parser import ExpressionParser


class ExpressionInterpreter:
    def __init__(self):
        pass


class MMMInterpreter(ExpressionInterpreter):
    def __init__(self):
        super(ExpressionInterpreter).__init__()

    def interpret_expression(self, tree):
        structure = tree.get_relations()
        return structure


if __name__ == "__main__":
    P = ExpressionParser()

    condition = """('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:NEUTRAL') OR
    ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:DRAIN')OR
    (('//423_EM-A01-JKT/SP.CV' = '423_JACKET_EM:NEUTRAL') AND
    ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:HOLD'))OR
    (('//423_EM-A01-JKT/SP.CV' = '423_JACKET_EM:DRAIN') AND
    ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:HOLD'));"""

    tree = P.parse_condition(condition)
    print(tree)
    # tr = tree.draw_tree()
    # tree.render_tree(tr)