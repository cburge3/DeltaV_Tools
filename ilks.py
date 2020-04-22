import xlsxwriter
from setup import convertfhxtoxml
from dv_parser import ExpressionParser
import re

data = []

"""To get all 3M interlocks and dump into approved documentation format"""

source_filename = "A_423"

params = open('outputs\\debug.txt', 'w')

root = convertfhxtoxml(source_filename, forcerebuild=False)

mods = root.findall(".//module_instance[@tag]")

mods += root.findall(".//module[@tag]")

# this is a critical expression to find any possible attributes that may be interlock related for class-based modules
paths = re.compile(r'(AT\d)|(DCC\d)|(CND\d{1,2})')

delay_ons = re.compile('(I|T)_DELAY_?ON(\d+)', re.IGNORECASE)
expression = re.compile('(I|T)_EXP(\d+)', re.IGNORECASE)
description = re.compile('(I|T)_DESC_?(\d+)', re.IGNORECASE)


def add_ilk_info_to_database(node, regex_search, field_search, data_entry, field_name, is_list=False):
    param_name = node.attrib['name']
    a = regex_search.search(param_name)
    num_exists = False
    if a is not None:
        num = str(a.groups()[1])
        field = node.find(field_search).text
        if is_list:
            placeholder = [field]
        else:
            placeholder = field
        for q in data_entry:
            if q['number'] != num:
                continue
            else:
                num_exists = True
            if num_exists and field_name not in q.keys():
                q[field_name] = placeholder
        if not num_exists:
            data_entry.append({'number': str(num), field_name: placeholder})
    return data_entry

# find all modules in the fhx

for mod in mods:
    ais = mod.findall(".//attribute_instance[@name]")
    params.write(mod.attrib['tag'] + '  ' + str(len(ais)) + '\n')
    if 'module_class' in mod.attrib.keys():
        class_name = mod.attrib['module_class']
        class_root = root.find(".//module_class[@name='" + class_name + "']")
        class_based_attrs = class_root.findall(".//attribute_instance[@name]")
        ais += class_root.findall(".//attribute_instance[@name]")
    data.append({'module': mod.attrib['tag']})
    data[-1]['description'] = mod.find(".//description").text
    data[-1]['ilk_data'] = []
    #
    for b in ais:
        # populate database with description data
        data[-1]['ilk_data'] = add_ilk_info_to_database(b, description, './/cv', data[-1]['ilk_data'], 'description',
                                                        is_list=True)
        # populate database with expression data
        data[-1]['ilk_data'] = add_ilk_info_to_database(b, expression, './/expression', data[-1]['ilk_data'],
                                                        'raw_expression', is_list=False)
        # populate database with delay on data
        data[-1]['ilk_data'] = add_ilk_info_to_database(b, delay_ons, './/cv', data[-1]['ilk_data'], 'on_delay',
                                                        is_list=False)

# we've extracted the raw data from the fhx now do some post-processing to convert it to a human readable format
# filter modules out of the report that don't actually have interlocks configured

keys = {'description', 'number', 'raw_expression'}

for mod in data:
    mod['ilk_data'] = [ilk for ilk in mod['ilk_data'] if keys.issubset(ilk.keys())]
    mod['ilk_data'] = [ilk for ilk in mod['ilk_data'] if ilk['description'][0] != "Not Used" and
                       ilk['description'][0] != str(ilk['number'])]
    for ilk in mod['ilk_data']:
        if 'on_delay' not in ilk.keys():
            ilk['on_delay'] = 0

# remove empty ilk_data entries

data = list(filter(lambda a: a['ilk_data'] != [], data))

# sort ilk_data entries by #
for mod in data:
    mod['ilk_data'].sort(key=lambda a: int(a['number']))

# placeholder code to get the first tag out of an expression

first_tag = re.compile(r'\d{3}_\w{1,3}-\d{1,3}')
P = ExpressionParser()

for mod in data:
    for ilk in mod['ilk_data']:
        ilk['cause_tag'] = []
        # populate cause tag
        conditions = P.parse_condition(ilk['raw_expression'], cond_object=True)
        print(ilk['raw_expression'])
        print(conditions)
        # tag = first_tag.search(ilk['raw_expression'])
        # if tag is not None:
        #     ilk['cause_tag'].append(tag.group())
        # else:
        #     ilk['cause_tag'].append('????')

        trip = ['something']
        ilk['trip'] = trip
        ilk['fail_state'] = "OFFFFF"

        # Create the interlock report from the collected data

headers = [['ILOCK', 'MODULE Name', '', 'INITIATING CONDITION(CAUSE)', '', '', 'Device', '', '', ''],
           ['REF NO.', 'Module Description', 'NO.', 'Interlock Description', 'DeltaV Tag Name', 'State(TRIP)',
            'Delay', 'Fail State', 'COMMENTS', 'TEST RESULTS']]

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook("outputs\\" + source_filename + "_interlocks.xlsx")

general = workbook.add_format({'font_name': 'Tahoma', 'font_size': 11})
general.set_bottom()
general.set_left()
general.set_right()
general.set_top()
headings = workbook.add_format({'bold': True, 'bg_color': 'D6DCE4', 'font_name': 'Tahoma', 'font_size': 11})
headings.set_bottom()
headings.set_left()
headings.set_right()
headings.set_top()
spacer = workbook.add_format({'bg_color': 'C0C0C0', 'font_name': 'Tahoma', 'font_size': 11})
spacer.set_bottom()
spacer.set_left()
spacer.set_right()
spacer.set_top()

worksheet = workbook.add_worksheet(source_filename)


# Start from the first cell. Rows and columns are zero indexed.
row = 1
col = 1

for i in headers:
    col = 1
    for j in i:
        worksheet.write(row, col, j, headings)
        col += 1
    row += 1

# description, cause tag, and state are all multi-line fields to allow chained conditions

ilk_dummy_data = [{'number': '1', 'description': ['interlock 1 is bad', '&&'], 'cause_tag': ['423_FC-55', '423_FC-66'],
                   'trip': ['ilk_expression', 'PV < 75'], 'on_delay': '2', 'fail_state': 'Close'},
                  {'number': '2', 'description': ['interlock 2 is OK'], 'cause_tag': ['340_FI-11'],
                   'trip': ['ilk_expression'], 'on_delay': '2', 'fail_state': 'Close'}]

max_col = len(headers[0]) + 1
for mod in range(0, len(data)):
    col = 1
    worksheet.write(row, col, mod + 1, general)
    worksheet.write(row, col + 1, data[mod]['module'], general)
    worksheet.write(row + 1, col, '', general)
    worksheet.write(row + 1, col + 1, data[mod]['description'], general)
    # for cnd in ilk_dummy_data:
    idx = 0
    for cnd in data[mod]['ilk_data']:
        if idx > 1:
            worksheet.write(row, col, '', general)
            worksheet.write(row, col + 1, '', general)
        lines = len(cnd['description'])
        worksheet.write(row, col + 2, cnd['number'], general)
        for l in range(0, lines):
            worksheet.write(row + l, col + 3, cnd['description'][l], general)
            worksheet.write(row + l, col + 4, cnd['cause_tag'][l], general)
            worksheet.write(row + l, col + 5, cnd['trip'][l], general)
        worksheet.write(row, col + 6, cnd['on_delay'], general)
        worksheet.write(row, col + 7, cnd['fail_state'], general)
        row += lines
        idx += 1
    if idx < 2:
        for cell in range(3, max_col):
            worksheet.write(row, cell, '', general)
        row += 1
    for cell in range(1, max_col):
        worksheet.write(row, cell, '', spacer)
    row += 1


col_widths = (1.22, 10.56, 44, 4.11, 50.78, 25.33, 34.22, 5.89, 17.89, 36, 16.89, 1.78)
for letter in range(0, len(col_widths)):
    worksheet.set_column(letter, letter, col_widths[letter])


# Write a total using a formula.
# worksheet.write(row, 0, 'Total')
# worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()
