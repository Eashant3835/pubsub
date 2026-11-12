from broker.protocol import encode_message
from broker.log import store_message
import os
import zlib

total = 0

path = "logs/test.log"
if os.path.exists(path):
    os.remove(path)

for text in ["Hi", "hello🙂", "Mitochondria is a powerhouse of the cell"]:
    encoded_message = encode_message(text)
    store_message("test", encoded_message)
    total = total + len(encoded_message) + 4

file_size = os.path.getsize(path)

print(total)
print(file_size)

def check(data):
    checksum_read = data[0:4]
    checksum = int.from_bytes(checksum_read, "big")
    length_read = data[4:8]
    length = int.from_bytes(length_read, "big")
    body_read = data[8:length + 8]
    body_checksum = zlib.crc32(length_read+body_read)
    if checksum == body_checksum:
        return("True")
    else:
        return("False")

with open(path, "rb") as f:
    data = f.read()
    print(check(data))
    damaged = bytearray(data)
    damaged[9] = 46
    print(check(damaged))