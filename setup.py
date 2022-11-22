import subprocess
import re
import lxml.etree
import os


"""Common functions used by other scripts here"""


def getfhxschema(xmlroot):
    s = xmlroot.find('.//schema')
    z = {}
    for m in s:
        z[m.tag] = m.text
    return z


def convertfhxtoxml(filename, sub_path=None):
    # using the root of the 'inputs' directory is assumed if no sub_path is given
    prsr = None
    input_dir = 'inputs'
    temp = 'temporary'
    full_path = input_dir
    if sub_path:
        full_path = input_dir + os.sep + sub_path
    if not os.path.exists(input_dir):
        os.mkdir(input_dir)
        os.mkdir("outputs")
    # renames fhx files to replace spaces to make batch scripting easier
    if ' ' in filename:
        if os.path.isfile(full_path + os.sep + filename.replace(' ', '_') + '.fhx'):
            os.remove(full_path + os.sep + filename.replace(' ', '_') + '.fhx')
        os.rename(full_path + os.sep + filename + '.fhx', full_path + os.sep + filename.replace(' ', '_') + '.fhx')
        filename = filename.replace(' ', '_')

    xmlfile = full_path + os.sep + filename + '.xml'
    tempfile = full_path + os.sep + temp + '.xml'
    # get timestamp from XML and check against fhx timestamp to determine whether to rebuild fhx or not
    if os.path.isfile(xmlfile):
        prsr = lxml.etree.XMLParser()
        root = lxml.etree.parse(xmlfile, parser=prsr)
        xml_time = root.find('.//schema').attrib['time']
        fhx = open(full_path + os.sep + filename + '.fhx', encoding='utf-16')
        re_timestamp = re.compile(r"time=(\d{10})")
        fhx_time = 0
        for line in fhx:
            t = re_timestamp.search(line)
            if t is not None:
                fhx_time = t.group(1)
                break
        if xml_time == fhx_time:
            print("Fhx matches existing xml - Not rebuilding xml")
            return root
    print("Generating xml from fhx file...")
    cwd = os.getcwd() + os.sep
    command = '..\\src_files\\deltav_xml.bat' + ' ' + filename + ' \"' + full_path + '\"'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         cwd=cwd + 'src_files')
    stdout, stderr = p.communicate()
    print("XML Parsing: " + stdout.decode())
    if not stderr is None:
        print(stderr.decode())
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
    if prsr is not None:
        prsr = lxml.etree.XMLParser()
    return lxml.etree.parse(xmlfile, parser=prsr)