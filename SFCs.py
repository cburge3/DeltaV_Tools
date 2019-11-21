from setup import convertfhxtoxml, getfhxschema
from docx import Document
from collections import defaultdict
import csv
import re

"""This can export SFC instructions into a docx table format or a csv table format"""


# TODO
# Check within confirms, delays, actions for references outside of a step
# Delay expressions that are either for the containing action or an action in a different step

format_type = dict()
format_type['csv'] = True
format_type['docx'] = False
format_type['code_verify'] = False
filename = "PURGES_419"
root = convertfhxtoxml(filename, forcerebuild=True)
print("Parsing SFC...")

fb_defs = root.findall('.//function_block_definition')
sfcs = list(filter(lambda a: not a.find('[sfc_algorithm]') is None, fb_defs))

if format_type['code_verify']:
    comments = re.compile('(?:\(\*[\s\S]*?\*\))|(?:REM.*)')
for sfc in sfcs:
    step_connections = sfc.findall('.//step_transition_connection')
    t_connections = sfc.findall('.//transition_step_connection')
    steps = sfc.findall('.//step')
    transitions = sfc.findall('.//transition')

    trans_conn_data = defaultdict(list)
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
        csv_out = open('outputs\\' + filename + '.csv', 'w', newline='')
        csv_writer = csv.writer(csv_out)
        csv_writer.writerow(['step name', 'action name', 'action description', 'action qualifier', 'action delay', 'action expression',
                            'action confirm'])
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
            if format_type['code_verify']:
                print('original')
                print(a_expression)
                # it's much easier to find expressions with the silly whole line ============ comments stripped
                cleaned = comments.sub('',a_expression)
                print('cleaned')
                # lines =
                print(cleaned.split('\n'))
                print('matches')
                # print(matches)
                # for m in matches:
                #     # if is an assignment expression NOT a comparison
                #     if m[1] is not '':
                #         print(s_name + ' ' + a_name + ' ' + m[0])
            # do csv stuff
            if format_type['csv']:
                csv_writer.writerow([s_name, a_name, a_description, a_qualifier, a_delay, a_expression, a_confirm])
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

