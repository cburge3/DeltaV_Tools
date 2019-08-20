import pandas as pd
from setup import convertfhxtoxml

filename = "R14102"

if __name__ == '__main__':
    root = convertfhxtoxml(filename)
    UCs = root.iter("batch_equipment_unit_module_class")
    table_names = []
    UIs = root.findall("batch_equipment_unit_module")
    data_tables = []
    for uc in UCs:
        print(uc.attrib['name'])
        alias_values = []
        alias_descriptions = []
        instances = []
        alias_names = [u.attrib['name'] for u in uc.findall(".//alias_definition")]
        [alias_values.append([]) for n in alias_names]
        [alias_descriptions.append([]) for n in alias_names]
        for unit_instance in UIs:
            if unit_instance.attrib['class'] == uc.attrib['name']:
                instances.append(unit_instance.attrib['name'])
                aliases = unit_instance.findall(".//alias_resolution")
                for m in aliases:
                    alias_name = m.attrib['name']
                    if alias_name in alias_names:
                        idx = alias_names.index(alias_name)
                    else:
                        continue
                    description = m.find('.//description')
                    if description is not None:
                        if description.text is None:
                            alias_descriptions[idx].append("")
                        else:
                            alias_descriptions[idx].append(str(description.text))
                    value = m.find('./value/value')
                    if value is not None:
                        if value.text is None:
                            alias_values[idx].append("Ignored")
                        else:
                            alias_values[idx].append(str(value.text))
        # build alias resolution tables
        data = {'unit instance': instances}
        for i in range(0, len(alias_names)):
            data[alias_names[i]] = alias_values[i]
        table = pd.DataFrame(data)
        table_names.append(uc.attrib['name'] + "_alias_values")
        table.set_index('unit instance')
        data_tables.append(table)
        # build description tables
        description_data = {'unit instance': instances}
        for i in range(0,len(alias_descriptions)):
            description_data[alias_names[i]] = alias_descriptions[i]
        table = pd.DataFrame(description_data)
        table_names.append(uc.attrib['name'] + "_alias_descriptions")
        table.set_index('unit instance')
        data_tables.append(table)
    for t in range(0,len(table_names)):
        data_tables[t].to_csv("\\outputs\\" + table_names[t] + ".csv")








