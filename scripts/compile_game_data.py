from cryptography.fernet import Fernet
import json
import os
import msgpack


here = os.path.dirname(__file__)
gameroot = f"{os.path.dirname(here)}/whitecrowparrot"
output = r"C:\Users\lio\Desktop\test\compiletest.json"

result = {}
count = 0
for root, _, filenames in os.walk(gameroot):
    for filename in filenames:
        filename = os.path.join(root, filename)
        ext = os.path.splitext(filename)[-1].lower()
        key = filename[len(gameroot) + 1:]
        if ext in (".json", ".ckl"):
            with open(filename, "r") as f:
                match ext:
                    case ".json":
                        result[key] = json.load(f)
                    case ".ckl":
                        result[key] = f.read()
        elif ext in (".png", ".ogg", ".wav"):
            with open(filename, "rb") as f:
                result[key] = f.read() #codecs.encode(f.read(), "base64")
        count += 1

result = msgpack.packb(result, use_bin_type=True)


with open(output, "wb") as f:
    f.write(result)
print(f"{count} files are compiler in {output}")