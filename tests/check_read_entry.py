from broker.log import read_entry, scan, store_message, LogCorruptionError
from broker.protocol import encode_message, PREFIX_SIZE
import os


topic = "logTest"
path = os.path.join("logs", topic + ".log")
if os.path.exists(path):
    os.remove(path)
messages = ["Hi", "hello🙂", "Mitochondria is a powerhouse of the cell"]
for text in messages:
    encoded_message = encode_message(text)
    store_message(topic, encoded_message)
starts = scan(path)[2]
for i in range(len(starts)):
    expected = encode_message(messages[i])[PREFIX_SIZE:]
    assert read_entry(path, starts, i) ==  expected, f"offset {i}"
assert read_entry(path, starts, len(starts)) is None, "past the end"
try:
    read_entry(path,starts,-1)
    assert False, "expected ValueError"
except ValueError:
    pass
assert read_entry(path, [], 0) is None, "empty starts"

original = open(path, "rb").read()
damaged = bytearray(original)
damaged[20] = 122
damaged_path = os.path.join("logs", "damaged.log")
with open(damaged_path,"wb") as f:
    f.write(damaged)
try:
    read_entry(damaged_path, starts, 1)
    assert False, "expected LogCorruptionError"
except LogCorruptionError:
    pass

assert read_entry(damaged_path, starts, 0) == encode_message(messages[0])[PREFIX_SIZE:]
assert read_entry(damaged_path, starts, 2) == encode_message(messages[2])[PREFIX_SIZE:]

torn_path = os.path.join("logs", "torn.log")
with open (torn_path, "wb") as f:
   f.write(original[:len(original) - 5])
torn_starts = scan(torn_path)[2]
assert torn_starts == starts[:2], "torn starts"
assert read_entry(torn_path, torn_starts, 1) == encode_message(messages[1])[PREFIX_SIZE:], "last surviving"
assert read_entry(torn_path, torn_starts, 2) is None, "torn past end"

new_offset = store_message(topic, encode_message("code"))
starts = scan(path)[2]
assert new_offset == len(starts) - 1, "returned offset"
assert read_entry(path, starts, new_offset) == encode_message("code")[PREFIX_SIZE:], "new entry readable"

os.remove(damaged_path)
os.remove(torn_path)
os.remove(path)