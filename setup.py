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


def convertfhxtoxml(filename, forcerebuild=False):
    subdir = 'inputs'
    temp = 'temporary'
    xmlfile = subdir + '\\' + filename + '.xml'
    tempfile = subdir + '\\' + temp + '.xml'
    # TODO
    # get timestamp from XML and check against fhx timestamp to determine whether to rebuild fhx or not
    if not os.path.isfile(xmlfile) or forcerebuild is True:
        print("Generating xml from fhx file...")
        cwd = os.getcwd() + '\\'
        command = '..\\src_files\\deltav_xml.bat' + ' ' + filename
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             cwd= cwd + 'src_files')
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
    else:
        print('Using existing xml file: ' + xmlfile)
    p = lxml.etree.XMLParser()
    return lxml.etree.parse(xmlfile, parser=p)