import os
import shutil

try:
    shutil.rmtree(r"C:\Users\lio\AppData\Local\Programs\Microsoft VS Code\resources\app\extensions\vscode_extension")
except FileNotFoundError:
    pass

corax_extension_path = os.path.join(os.path.dirname(__file__), '..', 'sdk', 'vscode_extension')
vscode_extention_path = r"C:\Users\lio\AppData\Local\Programs\Microsoft VS Code\resources\app\extensions\vscode_extension"

shutil.copytree(corax_extension_path, vscode_extention_path)

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
os.system("code .")