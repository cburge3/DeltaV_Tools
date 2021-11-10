from setup import convertfhxtoxml
import csv

filename = "RX"
data = dict()
data['phases'] = dict()
data['operations'] = dict()
data['unit_procedures'] = dict()
data['procedures'] = dict()
translation = {'OPERATION' : 'operations'}
root = convertfhxtoxml(filename)
phases = root.findall("batch_equipment_phase_class")
for p in phases:
    params = p.findall(".//batch_phase_parameter")
    parameters = dict()
    for pp in params:
        p_name = pp.attrib['name']
        parameters[p_name] = dict()
        # get parameter specific data
        parameters[p_name]['datatype'] = pp.attrib['type']
        parameters[p_name]['direction'] = pp.attrib['direction']
        d = pp.find('.//description')
        if d is not None:
            parameters[p_name]['description'] = d.text
        else:
            parameters[p_name]['description'] = ""
    # get more data about the recipe parameters only
    params = p.findall(".//attribute_instance")
    for pp in params:
        p_name = pp.attrib['name']
        if p_name in parameters.keys():
            # input parameters have more data than report parameters
            if parameters[p_name]['direction'] == 'INPUT':
                lo = pp.find('.//low')
                if lo is not None:
                    parameters[p_name]['low']= lo.text
                    parameters[p_name]['high'] = pp.find('.//high').text
                    parameters[p_name]['units'] = pp.find('.//units').text
                    parameters[p_name]['value'] = pp.find('.//cv').text
    data['phases'][p.attrib['name']] = parameters
recipes = root.findall('.//batch_recipe')
for r in recipes:
    r_name = r.attrib['name']
    recipe_type = r.attrib['type']
    params = r.findall(".//formula_parameter")
    parameters = dict()
    for pp in params:
        p_name = pp.attrib['name']
        parameters[p_name] = dict()
        # get parameter specific data
        parameters[p_name]['datatype'] = pp.attrib['type']
        d = pp.find('.//description')
        if d is not None:
            parameters[p_name]['description'] = d.text
        else:
            parameters[p_name]['description'] = ""
    # get more data about the recipe parameters only
    params = r.findall(".//attribute_instance")
    for pp in params:
        p_name = pp.attrib['name']
        if p_name in parameters.keys():
            parameters[p_name]['low']= pp.find('.//low').text
            parameters[p_name]['high'] = pp.find('.//high').text
            parameters[p_name]['units'] = pp.find('.//units').text
            parameters[p_name]['value'] = pp.find('.//cv').text
    # step = dict()
    # steps = r.findall('.//step')
    # for s in steps:
    #     s_name = s.attrib['name']
    #     s_def = s.attrib['definition']
    data[translation[recipe_type]][r_name] = parameters
# print(data)

csv_out = "outputs\\" + filename + "_output.csv"

ph = list(data['phases'].keys())[0]
# major workaround to get an input parameter rather than a report to get all of the keys
parm = list(data['phases'][ph].keys())[1]
headers = ['parameter', 'phase']
headers.extend(list(data['phases'][ph][parm].keys()))
with open(csv_out, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers, lineterminator='\n')
    writer.writeheader()
    for p in data['phases']:
        for param in data['phases'][p]:
            temp_dict = data['phases'][p][param].copy()
            temp_dict['phase'] = p
            temp_dict['parameter'] = param
            writer.writerow(temp_dict)
        # temp_dict = dict()
        # temp_dict = data['phases'][p].copy()
        # temp_dict['phase'] = p
        # print(temp_dict)
        # print(data['phases'][p].keys())
        # print(p,data['phases'][p])
        # for param in p.keys():
        #     print(param)
