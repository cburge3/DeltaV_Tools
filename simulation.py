from setup import convertfhxtoxml, getfhxschema
from math import trunc

"""This script is to generate simple tieback code for any class based modules in the configuration given
in <filename>.fhx"""

filename = "A_423"
root = convertfhxtoxml(filename)

data = {}
class_library = {}
max_lines_perblock = 190
s = open('src_files\\sim_module_template.txt', 'r')
m = open('src_files\\SIMULATION_template.fhx', mode='r', encoding='utf-16')
sim_module_template = s.read()
fhx_template = m.read()

wire_sources = {"@oon_logic@": "PDE1/OUT_D", "@ooff_logic@": "NDE1/OUT_D", "@c_logic@": "SIM_ON"}

act_template = '  ATTRIBUTE_INSTANCE NAME=\"ACT@act_num@/T_EXPRESSION\"\n\
{\n\
    VALUE { TYPE=ACTION EXPRESSION=\"@dv_logic_expression@\" }\n\
}\n'

act_fblock_template = '  FUNCTION_BLOCK NAME=\"ACT@act_num@\" DEFINITION=\"ACT\"\n\
  {\n\
    DESCRIPTION=\"Action\"\n\
    ID=598822322\n\
    RECTANGLE= { X=510 Y=@ycoord@ H=56 W=140 }\n\
  }'
y_interval = 100
y_start = 220

wire_template = '    WIRE SOURCE="@block_output@" DESTINATION="ACT@block@/IN_D" { }'

c_logic = {
    'EDC': '',
    # 'AO': '\'//@mod@/@block@/SIMULATE.SVALUE\' := \'//@mod@/@block@/OUT.CV\';\n',
    'AO': '\'//@mod@/@block@/SIMULATE.SVALUE\' := \'//@mod@/@block@/SP.CV\';\n',
    'DIWCALARM': '',
    'AIWCALARM': '',
    'DO': '\'//@mod@/@block@/SIMULATE_D.SVALUE\' := \'//@mod@/@block@/SP_D.CV\';\n',
    'AI': '',
    'PIDWCALARM': '',
    'PID': '',
    'DI': '',
    'DC': ''
}
oon_logic = {
    'EDC': '\'//@mod@/@block@/IGNORE_PV.CV\' := 1; \n\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2;\n',
    'AO': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 2;\n',
    'DIWCALARM': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2; \n\'//@mod@/@block@/SIMULATE_D.SSTATUS\' := GOOD;\n',
    'AIWCALARM': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 2;\n',
    'DO': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2;\n',
    'AI': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 2; \n\'//@mod@/@block@/SIMULATE.SSTATUS\' := GOOD;\n',
    'PIDWCALARM': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 2; \n\'//@mod@/@block@/SIMULATE.SSTATUS\' := GOOD;\n',
    'PID': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 2; \n\'//@mod@/@block@/SIMULATE.SSTATUS\' := GOOD;\n',
    'DI': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2;\n\'//@mod@/@block@/SIMULATE_D.SSTATUS\' := GOOD;\n',
    'DC': '\'//@mod@/DC_CTRL/IGN_PV.CV\' := 1; \n\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2;\n'
}
ooff_logic = {
    'EDC': '\'//@mod@/@block@/IGNORE_PV.CV\' := 0; \n\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 1;\n',
    'AO': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 1;\n',
    'DIWCALARM': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 1;\n',
    'AIWCALARM': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 1;\n',
    'DO': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 1;\n',
    'AI': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 1;\n',
    'PIDWCALARM': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 1;\n',
    'PID': '\'//@mod@/@block@/SIMULATE.ENABLE\' := 1;\n',
    'DI': '\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 2;\n',
    'DC': '\'//@mod@/DC_CTRL/IGN_PV.CV\' := 0; \n\'//@mod@/@block@/SIMULATE_D.ENABLE\' := 1;\n'
}

print('Building module class library...')
for c in root.findall('module_class'):
    io_blocks = []
    for fbs in ['EDC', 'DC', 'AI', 'AIWCALARM', 'AO', 'PID', 'PIDWCALARM', 'DI', 'DIWCALARM', 'DO']:
        b = []
        b = (c.findall('.//function_block[@definition=\"' + fbs + '\"]'))
        if b is not None:
            # in the event that there are duplicates of a function block in the module
            for block in b:
                io_blocks.append([block.attrib['definition'], block.attrib['name']])
    class_library[c.attrib['name']] = io_blocks

print('Linking instances to parent classes...')
for mod in root.findall('module_instance'):
    parent_class = mod.attrib['module_class']
    parent_area = mod.attrib["plant_area"].split('/')[0]
    # module templates will end up in this list with an area of "" so we drop them here
    if parent_area == '':
        continue
    module_name = mod.attrib["tag"]
    controller = mod.find(".//controller").text
    if parent_area not in list(data):
        data[parent_area] = []
    data[parent_area].append([module_name, parent_class, controller])

# TODO find non-class based control modules - maybe
for a in list(data):
    print('Creating simulation for area \"{}\" '.format(a))
    continuous_logic = ''
    oneshot_on_logic = ''
    oneshot_off_logic = ''
    area_sim = sim_module_template
    area_sim = area_sim.replace('@module_name@', a[0:min(min(len(a), 11), len(a))] + '_SIM')
    area_sim = area_sim.replace('@area_name@', a)
    area_sim = area_sim.replace('@description@', a + " simulation")
    # get the best controller to execute the simulation module
    mlist = data[a]
    ctrls = []
    # handle each module
    for m in mlist:
        # ignore modules that are unassigned to a node
        if m[2] is not None:
            # add 1 instance of controller to the list of controllers
            ctrls.append(m[2])
            for b in class_library[m[1]]:
                # compile entirety of needed logic with the logic templates
                continuous_logic += c_logic[b[0]].replace('@mod@', m[0]).replace('@block@', b[1])
                oneshot_on_logic += oon_logic[b[0]].replace('@mod@', m[0]).replace('@block@', b[1])
                oneshot_off_logic += ooff_logic[b[0]].replace('@mod@', m[0]).replace('@block@', b[1])
    max_count = 0
    best_ctrl = ''
    continuous_logic = continuous_logic.split('\n')
    oneshot_on_logic = oneshot_on_logic.split('\n')
    oneshot_off_logic = oneshot_off_logic.split('\n')
    # get most frequent controller for area
    for z in set(ctrls):
        if ctrls.count(z) > max_count:
            max_count = ctrls.count(z)
            best_ctrl = z
    # if no modules are assigned to a controller in the area don't assign the simulation either
    if best_ctrl is None:
        best_ctrl = ''
    area_sim = area_sim.replace('@ctrl@', best_ctrl)
    index = 0
    running_total_actblocks = 0
    logic_names = ["@oon_logic@", "@ooff_logic@", "@c_logic@"]
    y_coord = y_start - y_interval
    for logic_set in [oneshot_on_logic, oneshot_off_logic, continuous_logic]:
        index += 1
        if logic_set == ['']:
            logic_set = ''
        # estimate number of lines of code
        lines = len(logic_set)
        # calculate number of action blocks needed
        n_actblocks = trunc(lines / max_lines_perblock) + 1
        for r in range(1, n_actblocks + 1):
            logic_output = ''
            this_wire = ''
            this_fblock = ''
            running_total_actblocks += 1
            y_coord += y_interval
            start_line = int((r - 1) * max_lines_perblock)
            end_line = min(int(r * max_lines_perblock), lines)
            print("executing {} action block {} of {} out of {} total lines".
                  format(logic_names[index - 1], r, n_actblocks, lines))
            print("lines {} through {}".format(start_line, end_line))
            if start_line != end_line:
                logic_output = act_template.replace("@dv_logic_expression@", '\n'.join(logic_set[start_line:end_line]))
            else:
                logic_output = act_template.replace("@dv_logic_expression@", "A := B; \n")
            logic_output = logic_output.replace('@act_num@', str(running_total_actblocks))
            this_wire = wire_template.replace('@block_output@', wire_sources[logic_names[index - 1]])
            this_wire = this_wire.replace('@block@', str(running_total_actblocks))
            this_fblock = act_fblock_template.replace('@act_num@', str(running_total_actblocks))
            this_fblock = this_fblock.replace('@ycoord@', str(y_coord))
            # if this is the very last action block don't leave an insertion point for the next one
            if index == 3 and r == n_actblocks:
                print("finishing the area \"{}\" module".format(a))
                area_sim = area_sim.replace('@action_block@', logic_output)
                area_sim = area_sim.replace('@function_block@', this_fblock)
                area_sim = area_sim.replace('@wire_template@', this_wire)
            else:
                area_sim = area_sim.replace('@action_block@', logic_output + "\n  @action_block@")
                area_sim = area_sim.replace('@function_block@', this_fblock + "\n @function_block@")
                area_sim = area_sim.replace('@wire_template@', this_wire + "\n@wire_template@")
    fhx_template = fhx_template.replace('@module@', area_sim + '\n @module@')
fhx_template = fhx_template.replace('@module@', '')
schema = getfhxschema(root)
headers = {'@version@': 'version_str', '@mv@': 'major_version', '@mn@': 'minor_version', '@mi@': 'maintenance_version',
           '@bv@': 'build_version', '@bid@': 'build_id'}
for k in headers:
    fhx_template = fhx_template.replace(k, schema[headers[k]])
output_file = open('outputs\\' + filename + '_simulation.fhx', 'w')
output_file.write(fhx_template)


