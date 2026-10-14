import os
from broker.protocol import encode_message
import zlib

def store_message(topic, encoded_message):
    path = os.path.join("logs", topic + ".log")
    os.makedirs("logs", exist_ok=True)
    CHECKSUM_SIZE = 4
    checksum = zlib.crc32(encoded_message)
    crc_prefix = checksum.to_bytes(CHECKSUM_SIZE, 'big')
    crc_message = crc_prefix + encoded_message
    with open(path, "ab") as f:
        f.write(crc_message)
        f.flush()
        os.fsync(f.fileno())

store_message("news", encode_message({"payload": "hi"}))
store_message("news", encode_message({"payload": "bye"}))