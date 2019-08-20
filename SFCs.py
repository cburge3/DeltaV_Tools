from setup import convertfhxtoxml, getfhxschema
from docx import Document
from collections import defaultdict

filename = "DVP14201T2-XOUT"
root = convertfhxtoxml(filename)
doc = Document()
action_column_headings = ['Step', 'Action', 'Delay', 'Action Expression', 'Confirm Expression']
transition_column_headings = ['Transition', 'Condition']

fb_defs = root.findall('.//function_block_definition')

sfcs = list(filter(lambda a: not a.find('[sfc_algorithm]') is None, fb_defs))
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
    t = doc.add_table(rows=1, cols=len(action_column_headings))
    header = t.rows[0].cells
    for step in steps:
        for i in range(0, len(action_column_headings)):
            header[i].text = action_column_headings[i]
        actions = step.findall('.//action')
        num_actions = len(actions)
        action_index = 0
        first_cell = ''
        last_cell = ''
        for action in actions:
            action_row = t.add_row().cells
            if action_index == 0:
                first_cell = action_row[0]
                action_row[0].text = s_name
            action_index += 1
            if action_index == num_actions:
                last_cell = action_row[0]
            action_row[1].text = action.attrib['name']
            # either delay expression or delay time
            if action.find('.//delay_time') is not None:
                action_row[2].text = action.find('.//delay_time').text
            elif action.find('.//delay_expression') is not None:
                action_row[2].text = action.find('.//delay_expression').text
            else:
                print("Unknown delay type {}/{}".format(step.attrib['name'], action.attrib['name']))
                action_row[2].text = 'N/A'
            action_row[3].text = action.find('.//expression').text
            if action.find('.//confirm_expression') is not None:
                action_row[4].text = action.find('.//confirm_expression').text
            else:
                # No confirm used
                action_row[4].text = 'N/A'
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






doc.save('outputs\\SFC_report.docx')
