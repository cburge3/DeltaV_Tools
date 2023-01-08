from graphviz import Digraph
import os
from recipe_parameters import RecipeDatabase
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin'

db = RecipeDatabase('Lonza2')
data = db.db_load()
print(data['procedures'].keys())

print(data['procedures']['PR-SUM-MAIN'])


s = Digraph('structs', filename='structs.gv', node_attr={'shape': 'record'})

s.node('recipe1', r'{c|h |i |p }')

# s.edges([('struct1:f1', 'struct2:f0'), ('struct1:f2', 'struct3:here')])

# s.view()





