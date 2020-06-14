import re
from compilationEngine import CompilationEngine
import os
import sys
def output(filename, xml):
    with open('output/'+filename[:-5]+'.xml', 'w') as f:
        for i in xml:
            f.writelines(i+'\n')

if __name__ == "__main__":
    filename = sys.argv[1]
    if re.search('.jack',filename) != None:
        compiler = CompilationEngine(filename)
        xml = compiler.xml_code

        f = re.sub('.*/','',filename)
        output(f,xml)
    else:
        f_list = list(map(lambda x: filename +'/'+x,os.listdir(filename)))
        for f in f_list:
            if re.search('xml',f) != None:
                continue

            compiler = CompilationEngine(f)
            xml = compiler.xml_code
            f = re.sub('.*/','',f)
            output(f, xml)

