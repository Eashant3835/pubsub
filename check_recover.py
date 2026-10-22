import os
from broker.log import store_message, scan, recover, LogCorruptionError
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

damaged = bytearray(original)
damaged[20] = 122
damaged2 = bytearray(original)
damaged2[60] = 122
fake_path = "logs/does_not_exist.log"

def helper(label, data):
    with open(damaged_path,"wb") as f:
        f.write(data)
    before = open(damaged_path, "rb").read()
    try:
        result = recover(damaged_path)
    except LogCorruptionError as e:
        print(f"{label}, raised: {e}")
    else:
        print(f"{label}, returned: {result}")
    after = open(damaged_path, "rb").read()
    print(f"Change in size: {len(before) - len(after)}")
    print(f"Scan again: {scan(damaged_path)}")
    print(f"{label}, bytes unchanged: {len(before) == len(after)}")

print(recover(fake_path))
helper("chop 1 byte",original[:length - 1] )
helper("flipped mid stream byte", damaged)
helper("undamaged", original)