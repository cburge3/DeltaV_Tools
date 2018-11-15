import subprocess
import re
import lxml.etree
import os


def convertfhxtoxml(filename, forcerebuild=False):
    subdir = 'src_files'
    temp = 'temporary'
    xmlfile = subdir + '\\' + filename + '.xml'
    tempfile = subdir + '\\' + temp + '.xml'
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
    p = lxml.etree.XMLParser()
    return lxml.etree.parse(xmlfile, parser=p)