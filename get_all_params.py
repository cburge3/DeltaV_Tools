from setup import convertfhxtoxml
import re

filename = "DeltaV_System"
root = convertfhxtoxml(filename)
parameter_name = re.compile(r'RP(\d{3})_DESC')

p_name = 'name'
desc = 'description'

data = {}

for mc in root.findall("module_class"):
    module_name = mc.attrib["name"]
    data[module_name] = {p_name: {}, desc:{}}
    index = 0
    for target in mc.findall(".//attribute_instance[@name]"):
        m = parameter_name.match(target.attrib["name"])
        if m:
            index += 1
            description = target.find('.//cv')
            i = int(m.group(1))
            if description is not None:
                data[module_name][desc][i] = description.text
            data[module_name][p_name][i] = m.group(0)
    # if no interlocks were found in the module delete it from the dataset
    if index == 0:
        del data[module_name]

for mod in root.findall("module_instance"):
    module_name = mod.attrib["tag"]
    data[module_name] = {p_name:{}, desc:{}}
    index = 0
    for ilks in mod.findall(".//attribute_instance[@name]"):
        m = parameter_name.match(ilks.attrib["name"])
        if m:
            index += 1
            description = ilks.find('.//cv')
            i = int(m.group(1))
            if description is not None:
                data[module_name][desc][i] = description.text
            data[module_name][p_name][i] = m.group(0)
    # if no interlocks were found in the module delete it from the dataset
    if index == 0:
        del data[module_name]

# build report

report = open("outputs\\" + filename + "_Parameters.csv", 'w')
report.write(','.join(['module', 'num', desc, p_name])+'\n')

for m in list(data):
    module = data[m]
    d = module[desc]
    e = module[p_name]
    max_ilks = max(len(d), len(e))
    for n in range(1,max_ilks + 1):
        index = n
        output = ','.join([m, str(index)])+','
        try:
            output += d[index] + ','
        except KeyError:
            output += ','
        try:
            output += e[index]
        except KeyError:
            pass
        report.write(output + '\n')