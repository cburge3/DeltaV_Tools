import warnings
import re
import csv
import html
from setup import convertfhxtoxml

warnings.simplefilter(action='ignore', category=FutureWarning)

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

class Expression:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.data = {'left': self.left, 'right': self.right}

    def data_dict(self):
        return self.data

    def add_quotes(self, text):
        self.data['quotes'] = text


class Conditional(Expression):
    def __init__(self, left, comparator, right):
        super().__init__(left, right)
        assert comparator in {'=', '<>', '~=', '!=', '<', '>', '<=', '>='}
        self.data['comparator'] = comparator


class Assignment(Expression):
    def __init__(self, left, right):
        super().__init__(left, right)


class ExpressionParser:
    def __init__(self, **kwargs):
        self.comment = re.compile('(?:\(\*[\s\S]*?\*\))|(?:REM.*)')
        self.keywords = 'ABS,EXP,MAX,SHL,ACOS,EXPT,MIN,SHR,AND,EUP,MOD,SIGN,ASIN,FALSE,NOT,SIN,ASR16,FRACT,' \
                        'Option Explicit,SQRT,ATAN,GOOD,OR,STBT,AUTO,GOTO,OS,SYSSTAT,BAD,IF,PEU,TAN,CAS,IMAN,REM,THEN,' \
                        'COS,LIMITED_CONSTANT,ROL,TIME,DO,LIMITED_HIGH,ROR,TIME_TO_STR,ELSE,LIMITED_LOW,ROTL,TRUE,' \
                        'END_IF,LN,ROTL16,TRUNC,END_VAR,LO,ROTR,UNC,END_WHILE,LOG,ROTR16,VAR,LOG2,ROUND,XOR,MAN,' \
                        'SELSTR,WHILE'
        self.operands = '+, -, *, /, AND, OR, NOT, XOR, MOD, !, =,<>, ~=, !=, <, >, <=, >=, **, :=, (,), x?y:z, ~,' \
                        ' ^,&, %'
        self.assignment_op = re.compile('(.*)?:=(.*)?;')
        self.comparison_operators = re.compile('(' + '|'.join(['=','<>','~=','!=','<','>','<=','>=']) + ')')
        self.conditional_chunks = re.compile('(OR|AND|XOR)')
        self.path = re.compile(r"'(\/\/|\^\/|\/|\w+)(\w+)(\/|\w+)+\.?(\w+)'")
        self.strings = []
        self.assignments = []
        info = kwargs.get('info', None)


    def parse_assignment(self, text):
        return self.tokenize_action(text)

    def parse_path(self, text):
        return self.tokenize_path(text)

    def parse_condition(self, text, cond_object):
        return self.tokenize_condition(text, condition_object=cond_object)


    # for assignment type expressions
    def tokenize_action(self, expression):
        cleaned = self.comment.sub('', expression)
        # parse by character for string level
        quote_indices = []
        open_quote = 0
        action_list = []

        cleaned, quotes = self.sub_quotes(cleaned)

        # find assignments operators
        assignments = self.assignment_op.findall(cleaned)
        for m in assignments:
            sides = []
            for side in m:
                sides.append(side.strip())
            action_list.append(sides)
        return action_list

    # this is for condition type expressions
    def tokenize_condition(self, expression, condition_object=False):
        cleaned = self.comment.sub('', expression)
        # parse by character for string level
        condition_list = []
        # assignments = self.assignment_op.findall(cleaned)
        conditions, quotes = self.sub_quotes(cleaned)
        conds = self.conditional_chunks.split(conditions)
        for a in conds:
            if condition_object:
                s = self.comparison_operators.split(a)
                s = [b.strip() for b in s]
                condition_list.append(Conditional(left=s[0], right=s[2], comparator=s[1]))
            else:
                condition_list.append(self.comparison_operators.split(a))
        return condition_list


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

    # main code verification function


if __name__ == '__main__':
    P = ExpressionParser()

    s1 = html.unescape("&apos;//423_PC-A01/PID1/PV.CV&apos; &gt; &apos;//423_FV-110/TP01.CV&apos;")
    s2 = html.unescape("""&apos;^/ACT_IDX.CV&apos; := &apos;^/ACT_IDX.CV&apos; + 1;
&apos;^/MSG1.CV&apos; := &quot;Setting the EM to &quot; + &apos;^/A_COMMAND.CVS&apos;;
&apos;^/MSG2.CV&apos; := &quot;Set Ejector EM to Off&quot;;
&apos;^/MSG_TYPE.CV&apos; := &apos;_MSG_TYPE:INFO&apos;;
(*
=====================================================================================
Set Valves
=====================================================================================
*)
IF &apos;^/EM_EJECTOR/A_PV.CV&apos; != &apos;423_VACUUM_EM_2_1:OFF&apos; THEN
&apos;^/EM_EJECTOR/A_COMMAND.CV&apos; := &apos;423_VACUUM_EM_2_1:OFF&apos; ;
ELSE
ENDIF;
(*
-------------------------------------------------------------------------------------
Set Scratch Time
-------------------------------------------------------------------------------------
*)
&apos;^/TIME_SAVE.CV&apos; := &apos;S0100/TIME.CV&apos;;
(*
=====================================================================================
End of Code
=====================================================================================
*)""")
    print(P.parse_assignment(s2))
    c = P.parse_condition(s1, True)
    print(type(c))
    for l in c:
        print(P.tokenize_path(l.left))
        print(P.tokenize_path(l.right))
