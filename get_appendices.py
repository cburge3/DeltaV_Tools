from setup import convertfhxtoxml
import re
from csv import DictWriter

data = {}
source_filename = "324_EM-A02-XFR"
root = convertfhxtoxml(source_filename, forcerebuild=False)

fields = re.compile('(t|r|o)p\d{3,}_(value|min|max|desc)', re.IGNORECASE)

all_parameters = root.findall('.//attribute_instance')
all_parameters = filter(lambda p : fields.match(p.attrib['name']), all_parameters)
for p in all_parameters:
    name = p.attrib['name']
    nv = p.attrib['name'].split('_')
    if nv[0] not in data.keys():
        data[nv[0]] = {'name': nv[0]}
    value = p.find('.//cv')
    if value is None:
        value = p.find('.//string_value')
    if value is not None:
        value = value.text
        data[nv[0]][nv[1]] = value

with open('outputs\\' + source_filename + '_parameters.csv', 'w') as f:
    w = DictWriter(f, list('name,DESC,MIN,MAX,VALUE'.split(',')), lineterminator='\n')
    w.writeheader()
    for d in data.values():
        w.writerow(d)


