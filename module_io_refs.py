import subprocess
import re as re
import xml.etree.ElementTree as et
from os import remove

filename = 'AMODEL_DB_3_8_17'
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


def convertfhxtoxml():
    command = 'deltav_xml.bat' + ' ' + filename
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         cwd=r"C:\Users\cburge\PycharmProjects\DeltaV Tools\\src_files")
    stdout, stderr = p.communicate()
    # print(stdout, stderr)
    if p.returncode != 0:
        raise stderr


def cleanupxml():
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


def getfrommodules(topleveltag):
    # get all references to I/O from class baseed modules
    for mod in root.findall(topleveltag):
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


def unreferencedDSTs():
    u = DSTs - referencedDSTs
    unreferenced.writelines(e + '\n' for e in u)


if __name__ == '__main__':
    # steps to create the xml tree
    # convertfhxtoxml()
    # cleanupxml()

    tree = et.parse(tempfile)
    root = tree.getroot()
    DSTs = {chm.text for chm in root.findall(charmpath + analog) if chm.text is not None}
    # DSTs.update(chm.text for chm in root.findall(sischarmpath + analog) if chm.text is not None)
    DSTs.update([chm.attrib['name'] for chm in root.findall(charmpath + HART) if chm.attrib is not None])
    DSTs.update([chm.text for chm in root.findall(PROVOXpath + analog) if chm.text is not None])

    report = open(filename + '_report.csv', mode='w')
    unreferenced = open(filename + '_unref.csv', mode='w')

    # class based modules
    getfrommodules('module_instance')

    # non class based modules
    getfrommodules('module')

    # safety modules
    getfrommodules('sif_module')

    unreferencedDSTs()

    # remove(tempfile)


# get all references from non class based modules

# get all I/O
# old code that gets CIOC and baseplate numbers but is not really relevant for our excercise
# for chm in root.findall('charm'):
#     ioc = chm.find('simple_io_channel')
#     dst = ioc.find('device_signal_tag')
#     if dst.text is not None:
#         print(chm.attrib['card_slot'], chm.attrib['controller'], dst.text)




