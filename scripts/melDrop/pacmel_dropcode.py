# after extraction this code will be executed
# two special variables are available:
# _pacmel_dir: string path to the extracted folder in temp
#   make sure to delete this afterwards!
# _pacmel_files: list with string paths to the extracted files
import os, subprocess
from maya import cmds
usd = cmds.internalVar(usd=True)
for f in _pacmel_files:
    src = os.path.normpath(f)
    trg = os.path.join(usd, os.path.basename(f))
    if os.path.exists(trg):
        os.remove(trg)
    os.rename(f, trg)
os.rmdir(_pacmel_dir)
pacmel_path = os.path.normpath(os.path.join(usd, 'pacmel.py'))
result = cmds.promptDialog(
    m=('pacmel was just "installed" :D\n'
       'Open pacmel.py in your favorite script editor to see how it works! Cheers: eRiC'),
    t='pacmel', text=pacmel_path, button=['Explore', 'Confirm'])
if result == 'Explore':
    subprocess.Popen(['explorer.exe', '/select,', pacmel_path])
