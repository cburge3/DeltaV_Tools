import warnings
import re
import html
from graphviz import Digraph
from expression_tree import ExpressionTree
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
import time

# TODO
# CR = code review , Doc = Documentation
# CR - transitions that don't reference the immediately preceding step
# Doc - what actions are unit parameters written to
# CR - actions that wait on themselves
# CR - inline step timers that reference time from another step
# CR - A_COMMAND expressions with A_PV confirms not using the same named sets
# CR - proper delay structure in Actions and Exit action

# TODO
# Check within confirms, delays, actions for references outside of a step
# Delay expressions that are either for the containing action or an action in a different step
# Pull IF/THEN pairs out before checking assignment operators


# this is only meant to handle 1 SFC at a time

# ideally this can be modified to parse expressions and sub in English language independent of an SFC context

class Token:
    def __init__(self, text, kind):
        self.text = text
        self.kind = kind

    def __str__(self):
        # return "Token:{}:{}".format(self.kind, self.text)
        return self.text

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        a = other
        try:
            a = other.text
        finally:
            return self.text == other.text


class ExpressionParser:
    def __init__(self):
        self._comment = re.compile('(?:\(\*[\s\S]*?\*\))|(?:REM.*)')
        self._keywords = re.compile("|".join("""ABS,EXP,MAX,SHL,ACOS,EXPT,MIN,SHR,AND,EUP,MOD,SIGN,ASIN,FALSE,NOT,SIN,ASR16,FRACT,\
Option Explicit,SQRT,ATAN,GOOD,OR,STBT,AUTO,GOTO,OS,SYSSTAT,BAD,IF,PEU,TAN,CAS,IMAN,REM,THEN,\
COS,LIMITED_CONSTANT,ROL,TIME,DO,LIMITED_HIGH,ROR,TIME_TO_STR,ELSE,LIMITED_LOW,ROTL,TRUE,\
END_IF,LN,ROTL16,TRUNC,END_VAR,LO,ROTR,UNC,END_WHILE,LOG,ROTR16,VAR,LOG2,ROUND,XOR,MAN,\
SELSTR,WHILE""".split(',')))
        self._constants = re.compile(r"FALSE|TRUE|BAD|GOOD|LIMITED_CONSTANT|LIMITED_HIGH|LIMITED_LOW|"
                                     r"UNC|AUTO|CAS|IMAN|LO|MAN|OS|RCAS|ROUT", re.IGNORECASE)
        # self._const_values = [0,1,] BAD / GOOD have different values depending on whether they are used for assignment or comparison!!!
        # self._operands = '+, -, *, /, AND, OR, NOT, XOR, MOD, !, =,<>, ~=, !=, <, >, <=, >=, **, :=, (,), x?y:z, ~,' \
        #                 ' ^,&, %'
        self._functions = re.compile(r"""(?:ABS|EXP|MAX|ACOS|EXPT|MIN|MOD|SIGN|ASIN|NOT|SIN|SQRT|ATAN|TAN|COS|LN|LOG|
LOG2|ROUND|XOR)""", re.IGNORECASE)
        self._arithmetic_operators = re.compile(r"\+|-|\*{1,2}|\/|&|%")
        self._assignment_op = re.compile('(.*)?:=(.*)?;')
        self._comparison_operators = re.compile(r'(?:>=?|<(?:>|=)?|!=|~=|=)')
        self.boolean_ops = re.compile('(?:OR|AND|XOR)', re.IGNORECASE)
        # self._path = re.compile(r"'(\/\/|\^\/|\/|\w+)(\w+)(\/|\w+)+\.?(\w+)'")
        self._path = re.compile(r"'(?:\w|\/|\.|\#|\_|\^|\-)+'")
        self._number = re.compile(r"(?:\d|\.)+")
        self._named_set = re.compile(r"'(?:\_|\w|\#|\$|\-){1,40}:(?:\_|\s|\w|\#|\$|\-)+'")
        self._open_paren = re.compile(r"\(")
        self._close_paren = re.compile(r"\)")
        self._space = re.compile(r"\s+")
        self._semicolon = re.compile(r";")
        self.tokens_rex = {'space': self._space, 'open_p': self._open_paren, 'close_p': self._close_paren,
                           'comp_op': self._comparison_operators, 'bool_op': self.boolean_ops, 'dv_path': self._path,
                           'number': self._number, 'keyword': self._constants, 'math_op': self._arithmetic_operators,
                           'function': self._functions, 'named_set': self._named_set, 'semicolon': self._semicolon}
        self._operand_family = {'dv_path', 'number', 'keyword', 'named_set'}
        self._operator_family = {'comp_op', 'bool_op', 'math_op'}
        self._ignored_family = {'semicolon', 'space'}
        self._function_family = {'function'}

    def parse_assignment(self, text):
        return self.tokenize_action(text)

    def parse_path(self, text):
        return self.tokenize_path(text)

    def parse_condition(self, text):
        p = self.prep_condition(text)
        tokens = self.tokenize_condition(p)
        token_count, tree = self.parse_piece(tokens)
        if token_count != len(tokens):
            raise Exception("Parse Error: Not all tokens consumed")
        return tree

    def parse_piece(self, tokens):
        last_token = False
        tree = ExpressionTree()
        consumed = 0
        tk = 0
        while tk < len(tokens):
            # input()
            # temp = tree.draw_tree()
            # tree.render_tree(temp)
            last_token = (tk == len(tokens)-1)
            # print(tk, tokens[tk], last_token)
            if tokens[tk].kind == 'open_p':
                count, sub_tree = self.parse_piece(tokens[tk + 1:])
                if sub_tree.has_data():
                    tree.add_subtree(sub_tree)
                    if not tree.current_node_value().kind == 'function':
                        tree.set_active_node(sub_tree.get_root_node())
                tk += count
                consumed += count
                continue
            if tokens[tk].kind in self._operator_family:
                pos = tree.insert_parent(tokens[tk])
                tree.set_active_node(pos)
            if tokens[tk].kind in self._operand_family:
                temp = tree.add_leaf(tokens[tk])
                if tree.nodes[tree.get_active_node()].value.kind == 'bool_op':
                    tree.set_active_node(temp)
            if tokens[tk].kind in self._function_family:
                temp = tree.add_leaf(tokens[tk])
                # if tree.nodes[tree.get_active_node()].value.kind == 'bool_op':
                # tree.set_active_node(temp)
            if tokens[tk].kind == 'close_p':
                # 2 is for open and close parenthesis
                return tk + 2, tree
    # implied = True statement
            tk += 1
            consumed += 1
        # print(tree.get_relations())
        return consumed, tree

    # for assignment type expressions
    def tokenize_action(self, expression):
        cleaned = self._comment.sub('', expression)
        # parse by character for string level
        action_list = []
        cleaned, quotes = self.sub_quotes(cleaned)
        # find assignments operators
        assignments = self._assignment_op.findall(cleaned)
        for m in assignments:
            sides = []
            for side in m:
                sides.append(side.strip())
            action_list.append(sides)
        return action_list

    # this is for condition type expressions
    def prep_condition(self, expression, quotes=False):
        cleaned = self._comment.sub('', expression)
        conditions, quotes = self.sub_quotes(cleaned)
        if quotes:
            return conditions, quotes
        else:
            return conditions

    def tokenize_condition(self, expression):
        e = expression
        tokens = []
        while len(e) > 0:
            matched = False
            t = None
            for z in self.tokens_rex.keys():
                t = self.tokens_rex[z].match(e)
                if t:
                    if z not in self._ignored_family:
                        raw_string = e[t.span()[0]: t.span()[1]]
                        tokens.append(Token(raw_string, z))
                    e = e[t.span()[1]:]
                    matched = True
            if not matched:
                print(self._space.match(e))
                print(self._comparison_operators.match(e))
                raise Exception("Tokens: {} unexpected token:{}".format(tokens, e))
        return tokens

    def tokenize_path(self, path):
        path_characters = '|'.join(["^",":","\/","\.","'"])
        re.split(path_characters, path)
        pieces = re.split(path_characters, path)
        pieces = [a for a in pieces if len(a.strip()) >= 2]
        return pieces

    def sub_quotes(self, expression):
        open_quote = 0
        quote_indices = []
        for c in range(0, len(expression)):
            if expression[c] == '"' and open_quote == 0:
                open_quote = c
            elif expression[c] == '"' and open_quote != 0:
                quote_indices.append((open_quote, c+1))
                open_quote = 0
        quotes = []
        quote_dict = dict()
        if len(quote_indices) > 0:
            [quotes.append(expression[m[0]:m[1]]) for m in quote_indices]
        idx = 0
        cleaned = expression
        for m in range(0, len(quotes)):
            cleaned = expression.replace(quotes[m], "%String{0}%".format(idx))
            quote_dict[idx] = quotes[m]
            idx += 1
        return cleaned, quotes

warnings.simplefilter(action='ignore', category=FutureWarning)

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
