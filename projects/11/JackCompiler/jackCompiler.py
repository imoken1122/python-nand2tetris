import re
from compilationEngine import CompilationEngine
import os
import sys
def output(dirname=None,filename = None, xml = None):
    if dirname is None:
       with open(filename[:-5]+'1.vm', 'w') as f:
            for i in xml:
                f.writelines(i+'\n')
    else:
        with open(dirname+'/'+filename[:-5]+'.vm', 'w') as f:
            print(dirname+'/'+filename[:-5]+'.vm')
            for i in xml:
                f.writelines(i+'\n')

if __name__ == "__main__":
    filename = sys.argv[1]
    if re.search('.jack',filename) != None:
        compiler = CompilationEngine(filename)
        vm = compiler.vmWriter.vm_code

        f = re.sub('.*/','',filename)
        output(None,filename,vm)
    else:
        f_list = list(map(lambda x: filename +'/'+x,os.listdir(filename)))
        for f in f_list:
            if re.search('.jack',f) == None:
                continue
            compiler = CompilationEngine(f)

            vm = compiler.vmWriter.vm_code
            f = re.sub('.*/','',f)
            output(filename,f, vm)

