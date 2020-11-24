from utilities import format_number
def get_description(e):
    d = e.find('.//description')
    if d is not None:
        print(d.text)

# # this will get the function block diagrams instead of SFCs
# print(len(fb_defs))
# fbds = list(filter(lambda a: not a.find('[fbd_algorithm]') is None, fb_defs))
# print(len(fbds))
# for l in fbds:
#     print(l.attrib['name'])
#     get_description(l)
#
# # build a step / transition relationship graph
# graph = 'graph ER {\n'
# graph += 'node[shape = box]; '
# for s in steps:
#     graph += s.attrib['name'] + '; '
# graph += '\nnode [shape=ellipse]; '
# for t in transitions:
#     graph += t.attrib['name'] + '; '
# graph += '\n\n'
# for s in step_connections:
#     graph += s.attrib['step'] + ' -- ' + s.attrib['transition'] + ';\n'
# for t in t_connections:
#     graph += t.attrib['transition'] + ' -- ' + t.attrib['step'] + ';\n'
# graph += '}'
# print(graph)

for a in range(1,41):
    offset = 40
    n = format_number(3, a)
    l = n
    l = format_number(3, a + 3*offset)
    # print(R"'^/OP{}_VALUE.CV' := '^/RP{}_VALUE.CV';".format(n,n))
    # print("\t'^/OP{}_VALUE.CV' := '^/DRY-PARAM/OP{}_VALUE.CV';".format(n, l))
    print("'^/OP{}_VALUE.CV' = '^/DRY-PARAM/OP{}_VALUE.CV' AND".format(n, l))
    # print("'^/RP{}_VALUE.CV' = '^/OP{}_VALUE.CV' AND".format(n, l))
    # print("'^/RP{}_VALUE.CV' := '^/OP{}_VALUE.CV';".format(n, l))
    # print("'^/OP{}_VALUE.CV' := 0;".format(n))
    # print("'^/OP{}_VALUE.CV' = 0 AND".format(n))