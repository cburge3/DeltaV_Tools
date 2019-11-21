from setup import convertfhxtoxml
import re

filename = "R14102"
# TODO find AT interlocks in PID type modules
# Also remember what this script is for
ilock_name = re.compile(r'DCC1\$I_[A-z]*_?(\d+)')

root = convertfhxtoxml(filename)

exp = 'expressions'
desc = 'descriptions'

data = {}

for mod in root.findall("module_instance"):
    module_name = mod.attrib["tag"]
    data[module_name] = {exp:{}, desc:{}}
    index = 0
    for ilks in mod.findall(".//attribute_instance[@name]"):
        m = ilock_name.match(ilks.attrib["name"])
        if m:
            index += 1
            description = ilks.find('.//cv')
            expression = ilks.find('.//expression')
            if description is not None:
                data[module_name][desc][m.group(1)] = description.text
            if expression is not None:
                data[module_name][exp][m.group(1)] = expression.text
    # if no interlocks were found in the module delete it from the dataset
    if index == 0:
        del data[module_name]

# build report

report = open("outputs\\" + filename + "_Interlocks.csv", 'w')
report.write(','.join(['module', 'num', desc, exp])+'\n')

for m in list(data):
    module = data[m]
    d = module[desc]
    e = module[exp]
    max_ilks = max(len(d), len(e))
    for n in range(1,max_ilks):
        index = str(n)
        output = ','.join([m, index])+','
        try:
            output += d[index] + ','
        except KeyError:
            output += ','
        try:
            output += e[index] + ','
        except KeyError:
            output += ','
        report.write(output + '\n')

