def populatenamedset(named_set_root):
    d = dict()
    entries = named_set_root.findall('.//entry')
    for e in entries:
        d[int(e.attrib['value'])] = e.attrib['name']
    return d