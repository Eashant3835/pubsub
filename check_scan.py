import os
from broker.log import store_message, scan
from broker.protocol import encode_message

path = "logs/test.log"
if os.path.exists(path):
    os.remove(path)
damaged_path = "logs/test_damaged.log"
if os.path.exists(damaged_path):
    os.remove(damaged_path)

for text in ["Hi", "hello🙂", "Mitochondria is a powerhouse of the cell"]:
    encoded_message = encode_message(text)
    store_message("test", encoded_message)

original = open(path, "rb").read()
length = os.path.getsize(path)

def try_it(label, data):
    with open(damaged_path,"wb") as f:
        f.write(data)
    print(f"{label}, {scan(damaged_path)}")

damaged = bytearray(original)
damaged[20] = 122
damaged2 = bytearray(original)
damaged2[60] = 122
fake_path = "logs/does_not_exist.log"

try_it("undamaged", original)
try_it("empty",b"")
try_it("chop 1 byte",original[:length - 1] )
try_it("chop mid checksum", original[:41])
try_it("chop mid length", original[:45])
try_it("no body", original[:47])
try_it("flipped mid stream byte", damaged)
try_it("flipped last entry byte", damaged2)
print(scan(fake_path))