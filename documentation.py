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
# CR - missing ACT_IDX incrementing
# CR - improper mode setting / confirming

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
        self.ruleset['reference_to_wrong_step'] = True
        self.ruleset['action_bad_delay'] = True

    def give_datafiles(self, file):
        # this requires datafiles parsed by the SFC utility
        with open('outputs\\' + file + '_actions.csv', mode='r') as excel:
            actions = csv.DictReader(excel)
            for row in actions:
                self.read_actions(row)
        with open('outputs\\' + file + '_transitions.csv', mode='r') as excel:
            transitions = csv.DictReader(excel)
            for row in transitions:
                self.read_transitions(row)

    def read_actions(self, row_data):
        self.actions.append(row_data)

    def read_transitions(self, row_data):
        self.transtions.append(row_data)

    def check_against_rules(self):
        for action in self.actions:
            action['comments'] = ''
        for transition in self.transtions:
            transition['comments'] = ''

        if self.ruleset['action_bad_delay']:
            # first check if is a standard previous action state delay
            # if action['action delay']
            for a in range(1,len(self.actions)):
                action = self.actions[a]
                if action['action qualifier'] != "P":
                    continue
                d = action['action delay']
                tokens = self.tokenize_condition(d)
                for t in range(0, len(tokens)):
                    # check for delay with path, comparison, then named set
                    if tokens[t].kind == 'comp_op' and tokens[t-1].kind == 'dv_path' and tokens[t+1].kind == 'named_set':
                        path_tokens = self.tokenize_path(str(tokens[t-1]))
                        # check if the first item is an internal path and not a reference to elsewhere i.e. step name
                        if path_tokens[0].kind == 'local' and path_tokens[1].kind == 'path_piece':
                            if self.ruleset['reference_to_wrong_step']:
                                # 2nd token should be step name
                                if str(path_tokens[1]) != action['step name']:
                                    action['comments'] += "Reference to the wrong step in delay. "
                            if str(path_tokens[2]) != self.actions[a-1]['action name']:
                                action['comments'] += "Delay isn't referenced to the previous action. "

    def show_steps(self):
        pass

    def print_table(self):
        csv_out = "outputs\\" + csv_file + "_output.csv"
        with open(csv_out, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.actions[0].keys(), lineterminator='\n')
            writer.writeheader()
            for a in self.actions:
                writer.writerow(a)

if __name__ == '__main__':
    fhx = 'PH_RX_NAOH_CLEAN'
    root = convertfhxtoxml(fhx)
    D = SFCDocumenter(fhx)
    csv_file = fhx + '_compiled'
    P = CodeDocumenter()
    P.give_datafiles(csv_file)
    P.check_against_rules()
    P.print_table()
