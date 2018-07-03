import glob
import shutil

for f in glob.glob('*.py'):
    print f
    shutil.move(f,f+'.old')
    
