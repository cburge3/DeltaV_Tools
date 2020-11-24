# takes an expression tree object and interprets it into human readable expressions
# this particular implementation is for a 3M interlock documentation program

from dv_parser import ExpressionParser


class ExpressionInterpreter:
    def __init__(self):
        self._operand_family = {'dv_path', 'number', 'keyword', 'named_set'}
        self._operator_family = {'comp_op', 'bool_op', 'math_op'}
        self._function_family = {'function'}


class MMMInterpreter(ExpressionInterpreter):
    def __init__(self):
        super(ExpressionInterpreter).__init__()

    def interpret_expression(self, tree):
        structure = tree.get_relations()
        text = self._descend_tree(structure)
        return structure

    def _descend_tree(self, subtree):
        text = ''
        if len(subtree) < 2:
            raise Exception("Tree has no children")
        children = subtree[1]
        if children[1] is list:
            left_child = self._descend_tree(children[1])
        else:
            if subtree[0] in self._operator_family:
                pass





if __name__ == '__main__':
    P = ExpressionParser()

    # s1 = html.unescape("&apos;//423_PC-A01/PID1/PV.CV&apos; &gt; &apos;//423_FV-110/TP01.CV&apos;")
    # condition = """('S0180/PENDING_CONFIRMS.CV' = 0) AND
    # (* heres a random comment too *)
    # (('//#EM-DAYTK-JKT#/A_PV.CV' != '^/B_DAYTKJK_EM_CMD.CV') OR
    # ('//#EM-DAYTK#/A_PV.CV' != '^/B_DAYTNK_EM_CMD.CV') OR
    # ('//#TC-DAYTK-JKT#/PID1/SP_HI_LIM.CV' != '^/B_HFP_JKT_SPHLIM.CV') OR
    # ('//#PT-DAY-TANK#/PID1/MODE.ACTUAL' != RCAS) OR
    # ('//#PT-DAY-TANK#/PID1/RCAS_IN.CV' != '^/B_HFP_PRESS_SP.CV') OR
    #
    # ('//#EM-PIC-HTR#/A_PV.CV' !=  '^/B_PICHTR_EM_CMD.CV') OR
    # ('//#TC-PIC-HTR#/PID1/MODE.ACTUAL' != RCAS) OR
    # ('//#TC-PIC-HTR#/PID1/RCAS_IN.CV' != '^/B_PICHTR_TEMP_SP.CV') OR
    #
    # ('//#EM-JACKET#/A_PV.CV' != '^/B_JKT_EM_CMD.CV') OR
    # ('//#TC-JACKET#/PID1/MODE.ACTUAL' !=  CAS) OR
    # ('//#TC-JACKET#/SP_HI_LIM.CV' != '^/B_RX_JKT_SPHILIM.CV') OR
    #
    # ('//#EM-BATCH#/A_PV.CV' != '^/B_BATCH_EM_CMD.CV') OR
    # ('//#TC-BATCH#/PID1/MODE.ACTUAL' != RCAS) OR
    # ('//#TC-BATCH#/PID1/RCAS_IN.CV' != '^/B_RX_BATCHTMP_SP.CV'))"""

    # condition = """'//#EM-PIC-HTR#/A_PV.CV' !=  '^/B_PICHTR_EM_CMD.CV' OR
    # '//#TC-PIC-HTR#/PID1/MODE.ACTUAL' != RCAS"""

#     condition = """('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:NEUTRAL') OR
# ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:DRAIN')OR
# (('//423_EM-A01-JKT/SP.CV' = '423_JACKET_EM:NEUTRAL') AND
# ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:HOLD'))OR
# (('//423_EM-A01-JKT/SP.CV' = '423_JACKET_EM:DRAIN') AND
# ('//423_EM-A01-JKT/A_PV.CV' = '423_JACKET_EM:HOLD'));"""

#     condition = """'//423_FV-88-BYP/DO1/OUT_D.CV' = '3M_OffBypass:OFF' AND
# '//423_ZT-56/DI1/PV_D.CV' = True"""

    # condition = """TRUE = 1 AND FALSE = 0"""

    # condition = """('S0180/PENDING_CONFIRMS.CV' = 0) AND
    # (('//#EM-DAYTK-JKT#/A_PV.CV' != '^/B_DAYTKJK_EM_CMD.CV')
    # OR
    # ('//#EM-DAYTK#/A_PV.CV' != '^/B_DAYTNK_EM_CMD.CV'))"""

#     condition = """(('//423_FV-72-BYP/DO1/OUT_D.CV' = '3M_OffBypass:OFF'AND
# ('//423_PIC-239/PV.CV') <= '/TP03.CV'))"""

    condition = """('//423_FV227-304BYP/DO1/OUT_D.CV' = '3M_OffBypass:OFF') AND
(('//423_PIC-239/PID1/PV.CV' - '//423_PC-A01/PID1/PV.CV') < '/TP01.CV')"""

    condition = """(('//U_423_A01/BV018_VALUE.CV' = TRUE) AND
((ABS('//423_WT-250/NET_WEIGHT.CV')) >= '//423_FV-72/TP04.CV') AND
(ABS('//423_FQI-HFP/TOTAL.CV'- (ABS('//423_WT-250/NET_WEIGHT.CV'))) > '//423_FV-72/TP05.CV'))"""

    # condition = """ABS('//423_FQI-HFP/TOTAL.CV'- (ABS'//423_WT-250/NET_WEIGHT.CV')) > '//423_FV-72/TP05.CV'"""
    # print(P.parse_assignment(s2))
    c = P.parse_condition(condition)
    tr = c.draw_tree()
    print(c.get_relations())
    c.render_tree(tr)
    I = MMMInterpreter()
    print(I.interpret_expression(c))