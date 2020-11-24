import re
import csv
from setup import convertfhxtoxml
from dv_parser import ExpressionParser
from SFCs import SFCDocumenter

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

class CodeDocumenter(ExpressionParser):
    def __init__(self, **kwargs):
        ExpressionParser.__init__(self)
        self.actions = []
        self.transtions = []
        self.ruleset = dict()

    def give_datafiles(self, file):
        # this requires datafiles parsed by the SFC utility
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
        # self.actions[-1]['cleaned actions'] = self.tokenize_actions(self.actions[-1]['action expression'])

    def parse_transitions(self, row_data):
        self.transtions.append(row_data)

    # for assignment type expressions
    # def tokenize_actions(self, expression):
    #     cleaned = self._comment.sub('', expression)
    #     # parse by character for string level
    #     quote_indices = []
    #     open_quote = 0
    #     action_list = []
    #
    #     cleaned, quotes = self.sub_quotes(cleaned)
    #
    #     # find assignments operators
    #     assignments = self._assignment_op.findall(cleaned)
    #     for m in assignments:
    #         sides = []
    #         for side in m:
    #             sides.append(side.strip())
    #         action_list.append(sides)
    #     return action_list

    # main code verification function

    def check_against_rules(self):
        self.ruleset['reference_to_wrong_step'] = True
        # ruleset['reference_to_wrong_step'] = False
        self.ruleset['action_bad_delay'] = True
        self.ruleset['quick_document'] = True
        for action in self.actions:
            action['comments'] = ''
        for transition in self.transtions:
            transition['comments'] = ''
        # for key, value in self.ruleset:
        #     if value


        # if ruleset['quick_document']:
        #     # make mbr lookups
        #     self.lookups = {}
        #     mbrs = root.findall('.//module_block')
        #     for mbr in mbrs:
        #         self.lookups[mbr.attrib['name']] = mbr.attrib['module']
        #     check_mode = re.compile('req_mode', re.IGNORECASE)
        #     check_sp = re.compile('(sp\.cv)|(out\.cv)|(req_sp\.cv)', re.IGNORECASE)
        #     check_param = re.compile('(t|r|o)p\d{3,}_value', re.IGNORECASE)
        #     for action in self.actions:
        #         action['quick document'] = ''
        #         for a in action['cleaned actions']:
        #             if check_mode.search(a[0] + a[1]) is not None:
        #                 l = self.tokenize_path(a[0])
        #                 r = self.tokenize_path(a[1])
        #                 action['quick document'] += "Set {0} {1} to {2}, "\
        #                     .format(self.lookups[l[1]], self.lookups[l[2]], r[0])
        #             if check_sp.search(a[0]) is not None:
        #                 l = self.tokenize_path(a[0])
        #                 r = self.tokenize_path(a[1])
        #                 sp = ''
        #                 if r[-1].strip("'") == "CV":
        #                     sp = r[-2].strip("'")
        #                 else:
        #                     sp = r[-1].strip("'")
        #                 try:
        #                     target = self.lookups[l[2]]
        #                 except KeyError:
        #                     target = l[2]
        #                 action['quick document'] += "Set {0} {1} to {2}, ".format(self.lookups[l[1]], target, sp)
        #             if check_param.search(a[0]) is not None:
        #                 l = self.tokenize_path(a[0])
        #                 r = self.tokenize_path(a[1])
        #                 print(a,l,r)
        #                 print("Set {0} to {1}, ".format(l[1], r[0]))
        #                 print(a[0],a[1])
        #         action['quick document'] = action['quick document'][:-2]




        if self.ruleset['reference_to_wrong_step']:
            pass
            # # all_steps = set([m['step name'] for m in self.actions])
            # # rows in the table
            # for action in self.actions:
            #     # print(action['step name'], action['action name'], type(action), len(action['cleaned actions']))
            #     # source / destination pairs in actions
            #     for assignment_pairs in action['cleaned actions']:
            #         # source and destination in action pairs
            #         for side in assignment_pairs:
            #             step_reference = self.step_convention.search(side)
            #             if step_reference:
            #                 if step_reference.group() != action['step name']:
            #                     print('Step reference error found in ' + action['step name'] +
            #                           '/' + action['action name'])
            #                     action['comments'] += 'Step referenced outside of this step\n'

        if self.ruleset['action_bad_delay']:
            # first check if is a standard previous action state delay
            print(self.actions[0])
            # if action['action delay']
            for a in range(1,len(self.actions)):
                print(a)
                action = self.actions[a]
                if action['action qualifier'] != "P":
                    continue
                d = action['action delay']
                # print(d)
                tokens = self.tokenize_condition(d)
                # for t in tokens:
                #     print(t.kind,":", t)
                for t in range(0, len(tokens)):
                    # check for delay with path, comparison, then named set
                    if tokens[t].kind == 'comp_op' and tokens[t-1].kind == 'dv_path' and tokens[t+1].kind == 'named_set':
                        # print(tokens[t-1],tokens[t],tokens[t+1])
                        path_tokens = self.tokenize_path(str(tokens[t-1]))
                        # print(path_tokens)
                        # check if the first item is an internal path and not a reference to elsewhere i.e. step name
                        if path_tokens[0].kind == 'local' and path_tokens[1].kind == 'path_piece':
                            if str(path_tokens[1]) != action['step name']:
                                action['comments'] += "Reference to the wrong step in delay. "
                            if str(path_tokens[2]) != self.actions[a-1]['action name']:
                                action['comments'] += "Delay isn't referenced to the previous action. "

            # print(self.tokenize_condition(d))

            # for action in self.actions:
            #     self.tokenize_condition(action['action delay'])
            # for transition in self.transtions:
            #     print(self.tokenize_condition(transition['condition']))

    def show_steps(self):
        pass
        # for l in self.actions:
        #     print(l['cleaned actions'])
    def print_table(self):
        csv_out = "outputs\\" + csv_file + "_output.csv"
        with open(csv_out, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.actions[0].keys(), lineterminator='\n')
            writer.writeheader()
            for a in self.actions:
                writer.writerow(a)

if __name__ == '__main__':
    fhx = 'CELL2'
    root = convertfhxtoxml(fhx, forcerebuild=False)
    D = SFCDocumenter(fhx)
    csv_file = fhx + '_compiled'
    P = CodeDocumenter()
    P.give_datafiles(csv_file)
    P.check_against_rules()
    P.print_table()
    # P.show_steps()
