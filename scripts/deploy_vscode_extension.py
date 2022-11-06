import os
import shutil

path = "~/AppData/Local/Programs/Microsoft VS Code/resources/app/extensions/vscode_extension"
try:
    shutil.rmtree(os.path.expanduser(path))
except FileNotFoundError:
    pass

corax_extension_path = os.path.join(os.path.dirname(__file__), '..', 'sdk', 'vscode_extension')
vscode_extention_path = os.path.expanduser(path)

shutil.copytree(corax_extension_path, vscode_extention_path)

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
os.system("code .")
print("done")