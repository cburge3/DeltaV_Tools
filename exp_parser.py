import csv
import re

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

csv_file = 'PURGE_HFP_3G_419'

filename = 'outputs\\' + csv_file + '.csv'


# this is only meant to handle 1 SFC at a time

class SFCParser:
    def __init__(self, **kwargs):
        self.comment = re.compile('(?:\(\*[\s\S]*?\*\))|(?:REM.*)')
        self.assignment_op = re.compile('(.*)?:=(.*)?;')
        self.step_convention = re.compile('S\d+')
        self.conditional_flags = ['IF/THEN', 'WHILE/DO']
        self.strings = []
        self.assignments = []
        info = kwargs.get('info', None)
        self.actions = []
        # if info is not None:
        #     self.steps.append(info['step'])

    def parse(self, row_data):
        self.actions.append(row_data)
        # print(self.actions[-1]['step name'])
        self.actions[-1]['cleaned actions'] = self.parse_strings(self.actions[-1]['action expression'])

    def parse_strings(self, expression):
        cleaned = self.comment.sub('', expression)
        # parse by character for string level
        quote_indices = []
        open_quote = 0
        action_list = []
        for c in range(0, len(cleaned)):
            if cleaned[c] == '"' and open_quote == 0:
                open_quote = c
            elif cleaned[c] == '"' and open_quote != 0:
                quote_indices.append((open_quote, c+1))
                open_quote = 0
        quotes = []
        quote_dict = dict()
        if len(quote_indices) > 0:
            [quotes.append(cleaned[m[0]:m[1]]) for m in quote_indices]
            idx = 0
        for m in range(0, len(quotes)):
            cleaned = cleaned.replace(quotes[m], "%String{0}%".format(idx))
            quote_dict[idx] = quotes[m]
            idx += 1

        # find assignments operators
        assignments = self.assignment_op.findall(cleaned)
        for m in assignments:
            sides = []
            for side in m:
                sides.append(side.strip())
            action_list.append(sides)
        return action_list

    def check_against_rules(self):
        ruleset = dict()
        for action in self.actions:
            action['comments'] = ''
        ruleset['time_for_wrong_step'] = True
        ruleset['action_self_delayed'] = False
        print(len(self.actions))
        if ruleset['time_for_wrong_step']:
            # all_steps = set([m['step name'] for m in self.actions])
            # rows in the table
            for action in self.actions:
                print(action['step name'], action['action name'], type(action), len(action['cleaned actions']))
                print(action['cleaned actions'])
                # source / destination pairs in actions
                for assignment_pairs in action['cleaned actions']:
                    # source and destination in action pairs
                    for side in assignment_pairs:
                        # print(side)
                        step_reference = self.step_convention.search(side)
                        if step_reference:
                            # print(b)
                            if step_reference.group() != action['step name']:
                                print('Step reference error found in ' + action['step name'] +
                                      '/' + action['action name'])
                                action['comments'] += 'Step referenced outside of this step\n'

        if ruleset['action_self_delayed']:
            pass

    def show_steps(self):
        for l in self.actions:
            print(l['cleaned actions'])


class ConditionParser:
    def __init__(self):
        pass

P = SFCParser()
with open(filename, mode='r') as excel:
    f = csv.DictReader(excel)
    for row in f:
        P.parse(row)
P.check_against_rules()
    # P.show_steps()
