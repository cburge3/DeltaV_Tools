import xlsxwriter
from setup import convertfhxtoxml
from exp_parser import ExpressionParser
import re

data = []

"""To get all 3M interlocks and dump into approved documentation format"""

source_filename = "A_423"

params = open('outputs\\debug.txt', 'w')

root = convertfhxtoxml(source_filename, forcerebuild=False)

mods = root.findall(".//module_instance[@tag]")

mods_nc = (root.findall(".//module[@tag]"))

# this is a critical expression to find any possible attributes that may be interlock related for class-based modules
paths = re.compile(r'(AT\d)|(DCC\d)|(CND\d{1,2})')

delay_ons = re.compile('(I|T)_DELAY_ON(\d+)', re.IGNORECASE)
expression = re.compile('(I|T)_EXP(\d+)', re.IGNORECASE)
description = re.compile('(I|T)_DESC_?(\d+)', re.IGNORECASE)

# find all modules in the fhx

for mod in mods:
    ais = mod.findall(".//attribute_instance[@name]")
    ilk_data_nodes = []
    for z in ais:
        if paths.match(z.attrib['name']) is not None:
            ilk_data_nodes.append(z)
    if len(ilk_data_nodes) > 0:
        data.append({'module': mod.attrib['tag']})
        data[-1]['description'] = mod.find(".//description").text
        data[-1]['ilk_data'] = []
    else:
        continue

    # these 3 similar sections below may be able to be compressed into a single function
    # populate database with description data

    for b in ilk_data_nodes:
        param_name = b.attrib['name']
        params.write(param_name + '\n')
        d = description.search(param_name)
        if d is not None:
            num = int(d.groups()[1])
            num_exists = False
            field = b.find('.//cv').text
            for z in data[-1]['ilk_data']:
                if z['number'] != str(num):
                    continue
                else:
                    z['description'] = [field]
                    num_exists = True
            if not num_exists:
                data[-1]['ilk_data'].append({'number': str(num), 'description': [field]})
            continue
        # populate database with expression data
        e = expression.search(param_name)
        if e is not None:
            num = str(e.groups()[1])
            num_exists = False
            field = b.find('.//expression').text
            for z in data[-1]['ilk_data']:
                if z['number'] != num:
                    continue
                else:
                    z['raw_expression'] = field
                    num_exists = True
            if not num_exists:
                data[-1]['ilk_data'].append({'number': num, 'raw_expression': field})
            continue
        # populate database with delay on data
        do = delay_ons.search(param_name)
        if do is not None:
            num = str(do.groups()[1])
            num_exists = False
            field = b.find('.//cv').text
            for z in data[-1]['ilk_data']:
                if z['number'] != num:
                    continue
                else:
                    z['on_delay'] = [field]
                    num_exists = True
            if not num_exists:
                data[-1]['ilk_data'].append({'number': num, 'on_delay': [field]})
            continue



# add non classed based module interlock data
# if pieces of an expression exist in class instances we may need to go back to the class to put together a full
# interlock

for mod in mods_nc:
    ais = mod.findall(".//attribute_instance[@name]")
    ilk_data = []
    for z in ais:
        if paths.match(z.attrib['name']) is not None:
            ilk_data.append(z)
    if len(ilk_data) > 0:
        data.append({'module': mod.attrib['tag']})
        data[-1]['description'] = mod.find(".//description").text
        data[-1]['ilk_data'] = []
    else:
        continue
    for b in ilk_data:
        params.write(b.attrib['name'] + '\n')

# we've extracted the raw data from the fhx now do some post-processing to convert it to a human readable format
# filter modules out of the report that don't actually have interlocks configured

keys = ['description', 'number', 'raw_expression']

for mod in data:
    for ilk in mod['ilk_data']:
        for k in keys:
            if k not in ilk.keys():
                print(k, ilk)
                mod['ilk_data'].remove(ilk)
    for ilk in mod['ilk_data']:
        if ilk['description'] == "Not Used" or ilk['description'] == ilk['number']:
            mod['ilk_data'].remove(ilk)

    # placeholder code to get the first tag out of an expression

Parser = ExpressionParser()
first_tag = re.compile(r'\d{3}_\w{1,3}-\d{1,3}')

for mod in data:
    for ilk in mod['ilk_data']:
        # populate cause tag
        tag = first_tag.search(ilk['raw_expression'])
        if tag is not None:
            ilk['cause_tag'] = tag.string
        else:
            ilk['cause_tag'] = '????'

        trip = 'something'





        # Create the interlock report from the collected data

headers = [['ILOCK','MODULE Name','','INITIATING CONDITION(CAUSE)','','','Device','','',''],
['REF NO.','Module Description','NO.','Interlock Description','DeltaV Tag Name','State(TRIP)',
            'Delay','Fail State','COMMENTS','TEST RESULTS']]

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

# description, cause tag, and state are all multiline fields to allow chained conditions

ilk_dummy_data = [{'number': '1', 'description': ['interlock 1 is bad', '&&'], 'cause_tag': ['423_FC-55', '423_FC-66'],
                   'trip': ['ilk_expression', 'PV < 75'],'on_delay': '2', 'fail_state': 'Close'},
                {'number': '2', 'description': ['interlock 2 is OK'], 'cause_tag': ['340_FI-11'],
                 'trip': ['ilk_expression'], 'on_delay': '2', 'fail_state': 'Close'}]

max_col = 10
for mod in range(0,len(data)):
    col = 1
    worksheet.write(row, col, mod+1, general)
    worksheet.write(row, col + 1, data[mod]['module'], general)
    worksheet.write(row + 1, col + 1, data[mod]['description'], general)
    # for cnd in ilk_dummy_data:
    for cnd in data[mod]['ilk_data']:
        lines = len(cnd['description'])
        worksheet.write(row, col + 2, cnd['number'], general)
        for l in range(0,lines):
            worksheet.write(row + l, col + 3, cnd['description'][l], general)
            worksheet.write(row + l, col + 4, cnd['cause_tag'][l], general)
            worksheet.write(row + l, col + 5, cnd['trip'][l], general)
        worksheet.write(row, col + 6, cnd['on_delay'], general)
        worksheet.write(row, col + 7, cnd['fail_state'], general)
        row += lines
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
