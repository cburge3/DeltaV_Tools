from setup import getfhxschema
from setup import convertfhxtoxml

filename = "R14102"
root = convertfhxtoxml(filename)

a = getfhxschema(root)
print(a)