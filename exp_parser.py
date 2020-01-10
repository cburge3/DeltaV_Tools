import re
import csv

# TODO
# CR = code review , Doc = Documentation
# CR - transitions that don't reference the immediately preceding step
# Doc - what actions are unit parameters written to
# CR - actions that wait on themselves
# CR - inline step timers that reference time from another step
# CR - A_COMMAND expressions with A_PV confirms not using the same named sets
# CR - proper delay structure in Actions and Exit action

# TODO
# Pull IF/THEN pairs out before checking assignment operators

csv_file = 'PH_423_MONO_3G'


# this is only meant to handle 1 SFC at a time


class SFCParser:
    def __init__(self, file, **kwargs):
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
        self.step_convention = re.compile('S\d+')
        self.strings = []
        self.assignments = []
        info = kwargs.get('info', None)
        self.actions = []
        self.transtions = []
        with open('outputs\\' + file + '_actions.csv', mode='r') as excel:
            actions = csv.DictReader(excel)
            for row in actions:
                self.parse_actions(row)
        with open('outputs\\' + file + '_transitions.csv', mode='r') as excel:
            transitions = csv.DictReader(excel)
            for row in transitions:
                self.parse_transitions(row)

    def parse_actions(self, row_data):
        self.actions.append(row_data)
        self.actions[-1]['cleaned actions'] = self.tokenize_actions(self.actions[-1]['action expression'])

    def parse_transitions(self, row_data):
        self.transtions.append(row_data)

    def tokenize_path(self, path):
        pass

    # for assignment type expressions
    def tokenize_actions(self, expression):
        cleaned = self.comment.sub('', expression)
        # parse by character for string level
        quote_indices = []
        open_quote = 0
        action_list = []

        cleaned, quotes = self.sub_quotes(cleaned)

        # for c in range(0, len(cleaned)):
        #     if cleaned[c] == '"' and open_quote == 0:
        #         open_quote = c
        #     elif cleaned[c] == '"' and open_quote != 0:
        #         quote_indices.append((open_quote, c+1))
        #         open_quote = 0
        # quotes = []
        # quote_dict = dict()
        # if len(quote_indices) > 0:
        #     [quotes.append(cleaned[m[0]:m[1]]) for m in quote_indices]
        #     idx = 0
        # for m in range(0, len(quotes)):
        #     cleaned = cleaned.replace(quotes[m], "%String{0}%".format(idx))
        #     quote_dict[idx] = quotes[m]
        #     idx += 1

        # find assignments operators
        assignments = self.assignment_op.findall(cleaned)
        for m in assignments:
            sides = []
            for side in m:
                sides.append(side.strip())
            action_list.append(sides)
        return action_list

    # this is for condition type expressions
    def tokenize_condition(self, expression):
        cleaned = self.comment.sub('', expression)
        # parse by character for string level
        condition_list = []
        # assignments = self.assignment_op.findall(cleaned)
        conditions, quotes = self.sub_quotes(cleaned)
        conds = self.conditional_chunks.split(conditions)
        # for a in conds:
        #     condition_list.append(self.comparison_operators.split(a))
        for a in conds:
            condition_list.append(self.comparison_operators.split(a))
        # print(self.comparison_operators.pattern)
        # for m in conds:
        #     sides = []
        #     for side in m:
        #         sides.append(side.strip())
        #         condition_list.append(sides)
        return condition_list

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

    def check_against_rules(self):
        ruleset = dict()
        for action in self.actions:
            action['comments'] = ''
        for transition in self.transtions:
            transition['comments'] = ''
        ruleset['reference_to_wrong_step'] = True
        ruleset['reference_to_wrong_step'] = False
        ruleset['action_self_delayed'] = True
        if ruleset['reference_to_wrong_step']:
            # all_steps = set([m['step name'] for m in self.actions])
            # rows in the table
            for action in self.actions:
                # print(action['step name'], action['action name'], type(action), len(action['cleaned actions']))
                # source / destination pairs in actions
                for assignment_pairs in action['cleaned actions']:
                    # source and destination in action pairs
                    for side in assignment_pairs:
                        step_reference = self.step_convention.search(side)
                        if step_reference:
                            if step_reference.group() != action['step name']:
                                print('Step reference error found in ' + action['step name'] +
                                      '/' + action['action name'])
                                action['comments'] += 'Step referenced outside of this step\n'

        if ruleset['action_self_delayed']:
            # for action in self.actions:
            #     self.tokenize_condition(action['action delay'])
            for transition in self.transtions:
                print(self.tokenize_condition(transition['condition']))

    def show_steps(self):
        for l in self.actions:
            print(l['cleaned actions'])

P = SFCParser(csv_file)
P.check_against_rules()
    # P.show_steps()
