from setup import convertfhxtoxml
import json
import csv
import os


class RecipeDatabase:
    def __init__(self, database_name):
        self.db_name = database_name
        self.db_folder = "outputs\\"
        self.db_path = "{}{}_recipe_database.json".format(self.db_folder, self.db_name)
        self.report_path = "{}\\{}_reports".format(self.db_folder, self.db_name)
        self.levels = ['phases', 'operations', 'unit_procedures', 'procedures']
        self.parameter_types = {'BATCH_PARAMETER_REAL': "Real", "ENUMERATION_VALUE": "Named Set",
                                "BATCH_PARAMETER_INTEGER": "Integer", "UNICODE_STRING": "String"}
    def db_load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as object_storage:
                data = json.load(object_storage)
                print("Loading existing JSON recipe database for {}".format(self.db_name))
        else:
            with open(self.db_path, "a"):
                data = dict()
                data['phases'] = dict()
                data['operations'] = dict()
                data['unit_procedures'] = dict()
                data['procedures'] = dict()
                print("Creating new JSON database for {}".format(self.db_name))
        return data

    def load_full_directory(self, directory_path):
        full_path = 'inputs\\' + directory_path
        if os.path.exists(full_path):
            directory_list = os.listdir(full_path)
            print(directory_list)
            for f in directory_list:
                fs = f.split(".")
                if fs[1] == 'fhx':
                    self.load_fhx_file(fs[0], directory_path)

    def load_fhx_file(self, fhx_name, directory_path=None):
        data = self.db_load()
        print("Loading {} fhx file".format(fhx_name))
        translation = {'OPERATION': 'operations', 'UNIT_PROCEDURE': 'unit_procedures', 'PROCEDURE': 'procedures'}
        if directory_path:
            root = convertfhxtoxml(fhx_name, directory_path)
        else:
            root = convertfhxtoxml(fhx_name)
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
                            parameters[p_name]['low'] = lo.text
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
                    lo = pp.find('.//low')
                    # numeric values
                    if lo is not None:
                        parameters[p_name]['low'] = lo.text
                        parameters[p_name]['high'] = pp.find('.//high').text
                        parameters[p_name]['units'] = pp.find('.//units').text
                        parameters[p_name]['value'] = pp.find('.//cv').text
                    enum_set = pp.find('.//set')
                    # named sets
                    if enum_set is not None:
                        parameters[p_name]['set'] = pp.find('.//set').text
                        parameters[p_name]['value'] = pp.find('.//string_value').text
                    #     strings
                    if lo is None and enum_set is None:
                        parameters[p_name]['value'] = pp.find('.//cv').text
            # step = dict()
            # steps = r.findall('.//step')
            # for s in steps:
            #     s_name = s.attrib['name']
            #     s_def = s.attrib['definition']
            data[translation[recipe_type]][r_name] = parameters
        with open(self.db_path, "w") as object_storage:
            json.dump(data, object_storage)

    def kneat_rp_table(self):
        data = self.db_load()
        csv_out = self.report_path + "kneat_output.csv"
        headers = ['Recipe', 'Recipe Level', 'Parameter', 'Name', 'Description', 'Type',
                   'Range', 'Eng. Units', 'Default Value']

        with open(csv_out, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, lineterminator='\n', restval='', extrasaction='ignore')
            writer.writeheader()
            for level in self.levels:
                for recipe in data[level]:
                    for param in data[level][recipe]:
                        temp_dict = data[level][recipe][param].copy()
                        temp_dict["Recipe"] = recipe
                        temp_dict["Recipe Level"] = level
                        temp_dict['Name'] = param
                        temp_dict['Description'] = temp_dict['description']
                        temp_dict['Default Value'] = temp_dict['value']
                        temp_dict['Parameter'] = temp_dict['description']
                        if temp_dict['datatype'] == 'ENUMERATION_VALUE':
                            temp_dict['Range'] = "N/A"
                            temp_dict['Eng. Units'] = "N/A"
                            temp_dict['Type'] = self.parameter_types[temp_dict['datatype']] +\
                                                "\n({})".format(temp_dict['set'])
                        elif temp_dict['datatype'] == 'UNICODE_STRING':
                            temp_dict['Range'] = "N/A"
                            temp_dict['Eng. Units'] = "N/A"
                            temp_dict['Type'] = self.parameter_types[temp_dict['datatype']]
                        else:
                            temp_dict['Range'] = " {} - {}".format(temp_dict['low'], temp_dict['high'])
                            temp_dict['Eng. Units'] = temp_dict['units']
                            temp_dict['Type'] = self.parameter_types[temp_dict['datatype']]
                        writer.writerow(temp_dict)

    def bottom_up_csv(self):
        data = self.db_load()
        csv_out = self.report_path + "_output.csv"
        lowest = ''
        for k in list(data.keys()):
            lowest_level = list(data[k].keys())
            if lowest_level:
                lowest = k
                break
            else:
                print("No {} in database".format(k))

        headers = ['parameter', 'procedure', 'unit_procedure', 'operation', 'phase', 'datatype', 'description', 'low',
                   'high', 'units', 'value']

        with open(csv_out, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, lineterminator='\n', restval='', extrasaction='ignore')
            writer.writeheader()
            for p in data[lowest]:
                for param in data[lowest][p]:
                    temp_dict = data[lowest][p][param].copy()
                    temp_dict[lowest] = p
                    temp_dict['parameter'] = param
                    print(temp_dict)
                    writer.writerow(temp_dict)
            # temp_dict = dict()
            # temp_dict = data['phases'][p].copy()
            # temp_dict['phase'] = p
            # print(temp_dict)
            # print(data['phases'][p].keys())
            # print(p,data['phases'][p])
            # for param in p.keys():
            #     print(param)


if __name__ == "__main__":
    rd = RecipeDatabase("Lonza2")
    # rd.load_fhx_file("Recipes_all")
    rd.load_full_directory("22Nov22 Recipes")
    rd.kneat_rp_table()
