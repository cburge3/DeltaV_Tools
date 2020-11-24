# import re
# from utilities import format_number
# from setup import convertfhxtoxml
#
# filename = "_EM_C_PROC_CTRL"
# root = convertfhxtoxml(filename)
# parameter_name = re.compile(r'\wP(\d{3})_DESC')
#
# for target in root.findall(".//attribute_instance"):
#     m = parameter_name.match(target.attrib["name"])
#     if m:
#         print(m)
#
# f = open('inputs//_PC_130_CENT.fhx', encoding='utf-16')
# output = open('outputs//out.fhx', 'w')

import re
from utilities import format_number
f = open('inputs//_PC_130_CENT.fhx', encoding='utf-16')
output = open('outputs//out.fhx', 'w')
g = re.compile("(OP)(\d{3})(_\w+)1")
for line in f:
    print(line)
    matches = g.findall(line)
    if matches:
        m = matches[0]
        newline = line.replace(''.join(m)+'1', m[0]+str(format_number(3, int(m[1])+100))+m[2])
        print(newline)
        output.write(newline)
    else:
        output.write(line)

        # print(''.join(m)+'1')
        # print(m[0]+str(format_number(3, int(m[1])+100))+m[2])