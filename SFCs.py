from setup import convertfhxtoxml
from utilities import populatenamedset
from docx import Document
from collections import defaultdict
import csv
import re

"""This can export SFC instructions into a docx table format or a csv table format"""

source_filename = "324_EM-A02-XFR"

format_type = dict()
format_type['csv'] = True
format_type['docx'] = False
options = dict()
options['run_logic'] = True
options['abort_logic'] = True
options['stop_logic'] = True
options['hold_logic'] = True
options['restart_logic'] = True
options['compile_all_logic'] = True
options['classless_EM'] = True
logic_lookup = dict()
root = convertfhxtoxml(source_filename, forcerebuild=True)
unclassed_object = re.compile('__[\d\w]{8}_[\d\w]{8}__')

fb_defs = root.findall('.//function_block_definition')
sfcs = list(filter(lambda a: not a.find('[sfc_algorithm]') is None, fb_defs))
sfcs_to_test = set()

# TODO handle other types of SFCs other than just phase run logic

phase_classes = root.findall('.//batch_equipment_phase_class')
module_instances = root.findall('.//module')



def add_logic_to_list(composite_name):
    for phase in phase_classes:
        definition = phase.find(".//function_block[@name='" + composite_name + "']").attrib['definition']
        sfcs_to_test.add(definition)
        if unclassed_object.match(definition):
            logic_lookup[definition] = phase.attrib['name']

if options['run_logic']:
    add_logic_to_list('RUN_LOGIC')
if options['abort_logic']:
    add_logic_to_list('ABORT_LOGIC')
if options['stop_logic']:
    add_logic_to_list('STOP_LOGIC')
if options['hold_logic']:
    add_logic_to_list('HOLD_LOGIC')
if options['restart_logic']:
    add_logic_to_list('RESTART_LOGIC')

if options['classless_EM']:
    for module in module_instances:
        flag = module.find(".//is_equipment_module")
        if flag is not None and flag.text == "T":
            commands = module.find(".//command_set").text
            command_set = root.find(".//enumeration_set[@name='" + commands + "']")
            ns = populatenamedset(command_set)
            definitions = module.findall(".//function_block")
            for d in definitions:
                definition = d.attrib['definition']
                if unclassed_object.match(definition) is not None:
                    cmd_match = re.search('\d+', d.attrib['name'])
                    if cmd_match is not None:
                        command_num = int(cmd_match[0])
                        logic_lookup[definition] = module.attrib['tag'] + ':' + ns[command_num]
                        sfcs_to_test.add(definition)
        else:
            break

if options['compile_all_logic']:
    csv_all_actions = open('outputs\\' + source_filename + '_compiled_actions.csv', 'w', newline='')
    csv_all_transitions = open('outputs\\' + source_filename + '_compiled_transitions.csv', 'w', newline='')
    csv_writer_actions_a = csv.writer(csv_all_actions)
    csv_writer_trans_a = csv.writer(csv_all_transitions)
    csv_writer_actions_a.writerow(['object name', 'step name', 'action name', 'action description', 'action qualifier',
                                         'action delay', 'action expression', 'action confirm'])
    csv_writer_trans_a.writerow(
                ['object name', 'transition name', 'transition description', 'condition', 'upstream connections',
                 'downstream connections'])
#     sfcs = list(filter(lambda a: unclassed_object.match(a.attrib['name']), sfcs))

# print(sfcs_to_test)
idx = 0
for sfc in sfcs:
    sfc_id = sfc.attrib['name']
    print(sfc_id)
    common_name = sfc_id
    if sfc_id in sfcs_to_test:
        if sfc_id in logic_lookup.keys():
            common_name = logic_lookup[sfc_id]
        idx +=1
        filename = common_name
        # print("Parsing SFC {0} {1} of {2}".format(sfc.attrib['name'], sfcs.index(sfc) + 1, len(sfcs)))
        print("Parsing SFC {0} {1} of {2}".format(filename, idx, len(sfcs_to_test)))
        step_connections = sfc.findall('.//step_transition_connection')
        t_connections = sfc.findall('.//transition_step_connection')
        steps = sfc.findall('.//step')
        transitions = sfc.findall('.//transition')

        trans_conn_data = defaultdict(list)
        # parse transitions
        for transition in transitions:
            t_name = transition.attrib['name']
            for tcs in t_connections:
                if t_name == tcs.attrib['transition']:
                    trans_conn_data[t_name].append(tcs.attrib['step'])

        step_conn_data = defaultdict(list)
        for step in steps:
            s_name = step.attrib['name']
            for scs in step_connections:
                if s_name == scs.attrib['step']:
                    step_conn_data[s_name].append(scs.attrib['transition'])
        # # create the tables for action logic
        if format_type['docx']:
            doc = Document()
            action_column_headings = ['Step', 'Action', 'Delay', 'Action Expression', 'Confirm Expression']
            transition_column_headings = ['Transition', 'Condition']
            t = doc.add_table(rows=1, cols=len(action_column_headings))
            header = t.rows[0].cells
        if format_type['csv']:
            csv_out_actions = open('outputs\\' + filename + '_actions.csv', 'w', newline='')
            csv_out_transitions = open('outputs\\' + filename + '_transitions.csv', 'w', newline='')
            csv_writer_actions = csv.writer(csv_out_actions)
            csv_writer_actions.writerow(['step name', 'action name', 'action description', 'action qualifier',
                                         'action delay', 'action expression', 'action confirm'])
            csv_writer_trans = csv.writer(csv_out_transitions)
            csv_writer_trans.writerow(
                ['transition name', 'transition description', 'condition', 'upstream connections',
                 'downstream connections'])
        for tr in transitions:
            t_name = ''
            t_expression = ''
            t_previous = ''
            t_previous_all = []
            t_description = ''
            t_name = tr.attrib['name']
            if tr.find('.//expression') is not None:
                t_expression = tr.find('.//expression').text
            if tr.find('.//description') is not None:
                t_description = tr.find('.//description').text
            for s in step_conn_data.keys():
                if t_name in step_conn_data[s]:
                    t_previous_all.append(s)
            t_previous = ','.join(t_previous_all)
            t_next = ','.join(trans_conn_data[t_name])
            if format_type['csv']:
                csv_writer_trans.writerow([t_name, t_description, t_expression, t_previous, t_next])
                if options['compile_all_logic']:
                    csv_writer_trans_a.writerow([common_name, t_name, t_description, t_expression, t_previous, t_next])
        for step in steps:
            s_name = step.attrib['name']
            actions = step.findall('.//action')
            action_index = 0
            num_actions = len(actions)
            if format_type['docx']:
                for i in range(0, len(action_column_headings)):
                    header[i].text = action_column_headings[i]
                first_cell = ''
                last_cell = ''
            for action in actions:
                a_name = action.attrib['name']
                a_qualifier = ''
                a_delay = 'N/A'
                a_confirm = 'N/A'
                a_expression = action.find('.//expression').text
                # either delay expression or delay time
                if action.find('.//delay_time') is not None:
                    a_delay = action.find('.//delay_time').text
                elif action.find('.//delay_expression') is not None:
                    a_delay = action.find('.//delay_expression').text
                if action.find('.//qualifier') is not None:
                    a_qualifier = action.find('.//qualifier').text
                if action.find('.//delay_time') is not None:
                    a_delay = action.find('.//delay_time').text
                if action.find('.//confirm_expression') is not None:
                    a_confirm = action.find('.//confirm_expression').text
                if action.find('.//description') is not None:
                    a_description = action.find('.//description').text
                if format_type['csv']:
                    csv_writer_actions.writerow([s_name, a_name, a_description, a_qualifier, a_delay, a_expression, a_confirm])
                    if options['compile_all_logic']:
                        csv_writer_actions_a.writerow(
                            [common_name, s_name, a_name, a_description, a_qualifier, a_delay, a_expression, a_confirm])
                # make docx table
                if format_type['docx']:
                    action_row = t.add_row().cells
                    if action_index == 0:
                        first_cell = action_row[0]
                    action_row[0].text = s_name
                    action_index += 1
                    if action_index == num_actions:
                        last_cell = action_row[0]
                    action_row[1].text = a_name
                    action_row[2].text = a_delay
                    action_row[3].text = a_expression
                    action_row[4].text = a_confirm
                    if action_index != 0:
                        first_cell.merge(last_cell)
                    t_header_row = t.add_row().cells
                    t_header_row[1].merge(t_header_row[4])
                    for i in range(0, len(transition_column_headings)):
                        t_header_row[i].text = transition_column_headings[i]
                    for next_t in step_conn_data[s_name]:
                        trans_row = t.add_row().cells
                    trans_row[0].text = next_t
                    my_expression = ''
                    for tr in transitions:
                        if tr.attrib['name'] == next_t:
                            my_expression = tr.find('expression').text
                        trans_row[1].text = my_expression
                        trans_row[1].merge(trans_row[4])
if format_type['docx']:
    doc.save('outputs\\SFC_report.docx')

