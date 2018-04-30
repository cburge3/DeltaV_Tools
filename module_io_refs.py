import subprocess
import re
from lxml.etree import XMLParser, parse, tounicode
import os

filename = "DeltaV_System20180313"
subdir = 'src_files'
temp = 'temporary'
xmlfile = subdir + '\\' + filename + '.xml'
tempfile = subdir + '\\' + temp + '.xml'

charmpath = 'charm/simple_io_channel/'
analog = 'device_signal_tag'
HART = 'hart_device_signal_tag'
PROVOXpath = 'provox_control_io_card/provox_control_io_channel/'
sischarmpath = 'sis_charm/simple_io_channel/device_signal_tag'
referencedDSTs = set()


def convertfhxtoxml(forcerebuild=False):
    if not os.path.isfile(xmlfile) or forcerebuild is True:
        print("Generating xml from fhx file...")
        cwd = os.getcwd() + '\\'
        command = 'deltav_xml.bat' + ' ' + filename
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             cwd= cwd + subdir)
        stdout, stderr = p.communicate()
        print(stdout, stderr)
        # remove escaped xml characters - probably overkill but we don't care about these
        bads = re.compile(r'&#\d+?;')
        # remove high/low unicodes not accepted by et.parse
        out = open(tempfile, mode='w')
        with open(xmlfile, encoding='utf-8') as file:
            for l in file:
                a = ''
                for c in l:
                    if 31 < ord(c) < 126:
                        a += c
                    a = re.sub(bads, '', a)
                out.write(a + '\x0A')
        if p.returncode != 0:
            raise stderr
        out.close()
        os.replace(cwd + tempfile, cwd + xmlfile)
    else:
        print('Using existing xml file: ' + xmlfile)


def linkexternalcomposites(elem):
    # this is currently used to link linked composites within an sif_module back to the linked composite (class?)
    # further back in the fhx given a function block unique identifier.  It is not understood why these composites
    #  don't fall under the sif_module xml tag
    fbuid = re.compile(r'__(?:[0-9]|[A-F]){8}_(?:[0-9]|[A-F]){8}__')
    for fbs in elem.findall('function_block'):
        if 'definition' in fbs.attrib:
            if fbuid.match(fbs.attrib['definition']):
                for fbdef in root.findall('sis_function_block_definition'):
                    if fbdef.attrib['name'] == fbs.attrib['definition']:
                        elem.append(fbdef)


def getfrommodules(topleveltag, report):
    # get all references to I/O from modules with xml tag: topleveltag
    for mod in root.findall(topleveltag):
        linkexternalcomposites(mod)
        for tag in mod.iter('ref'):
            if tag.text is not None:
                try:
                    if tag.text.split('/')[2] in DSTs:
                        t = tag.text.split('/')[2]
                        report.writelines(mod.attrib['tag'] + ',' + t + '\n')
                        referencedDSTs.add(t)
                except IndexError:
                    # properly formatted DST references will include "//" before the DST name so we use slice[2]
                    pass


def unreferencedDSTs(unreferenced):
    u = DSTs - referencedDSTs
    unreferenced.writelines(e + '\n' for e in u)

def PROVOXIOInfo():
    IOinfo = open(filename + '_PROVOX_IO.csv', mode='w')
    f = PROVOXpath.split('/')[0]
    c = PROVOXpath.split('/')[1]
    for card in root.findall(f):
        for channel in card.findall(c):
            for dst in channel.findall(analog):
                if dst.text is not None:
                    IOinfo.writelines(','.join([card.attrib['controller'], card.attrib['file'], card.attrib['card_slot'],
                      channel.attrib['position'], dst.text]) + '\n')


if __name__ == '__main__':
    # steps to create the xml tree
    convertfhxtoxml()
    p = XMLParser()
    root = parse(xmlfile, parser=p)

    PROVOXIOInfo()

    # adds standard DSTs
    DSTs = {chm.text for chm in root.findall(charmpath + analog) if chm.text is not None}
    # adds SIS DSTs
    DSTs.update(chm.text for chm in root.findall(sischarmpath) if chm.text is not None)
    # adds HART DSTs
    DSTs.update([chm.attrib['name'] for chm in root.findall(charmpath + HART) if chm.attrib is not None])
    # adds PROVOX I/O DSTs
    DSTs.update([chm.text for chm in root.findall(PROVOXpath + analog) if chm.text is not None])

    report = open(filename + '_report.csv', mode='w')
    unreferenced = open(filename + '_unref.csv', mode='w')

    # class based modules
    getfrommodules('module_instance', report)

    # non class based modules
    getfrommodules('module', report)

    # safety modules
    getfrommodules('sif_module', report)

    unreferencedDSTs(unreferenced)

    # os.remove(tempfile)





