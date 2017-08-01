import subprocess
import re as re
import xml.etree.ElementTree as et

filename = 'Sulfone_31Jul'
subdir = 'src_files'
temp = 'temporary'
xmlfile = subdir + '\\' + filename + '.xml'
tempfile = subdir + '\\' + temp + '.xml'


def convertfhxtoxml():
    command = 'deltav_xml.bat' + ' ' + filename
    p = subprocess.Popen(command, shell=True, stdout = subprocess.PIPE,
                         cwd=r"C:\Users\cburge\PycharmProjects\DeltaV Tools\\src_files")

    stdout, stderr = p.communicate()
    # print(stdout, stderr)
    if p.returncode != 0:
        raise stderr# is 0 if success


def cleanupxml():

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
                        report.writelines(mod.attrib['tag'] + ', ' + tag.text.split('/')[2] + '\n')
                except IndexError:
                    pass


convertfhxtoxml()
cleanupxml()

tree = et.parse(tempfile)
root = tree.getroot()
DSTs = {chm.text for chm in root.findall('charm/simple_io_channel/device_signal_tag') if chm.text is not None}

report = open('report.csv', mode='w')

# class based modules
getfrommodules('module_instance')

# non class based modules
getfrommodules('module')


# get all references from non class based modules

# get all I/O
# old code that gets CIOC and baseplate numbers but is not really relevant for our excercise
# for chm in root.findall('charm'):
#     ioc = chm.find('simple_io_channel')
#     dst = ioc.find('device_signal_tag')
#     if dst.text is not None:
#         print(chm.attrib['card_slot'], chm.attrib['controller'], dst.text)




