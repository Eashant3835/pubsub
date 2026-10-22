import os
from broker.protocol import encode_message
import zlib

CHECKSUM_SIZE = 4
LENGTH_SIZE = 4
CLEAN_END = "clean end"
TORN_TAIL = "torn tail"
CORRUPTION = "corruption"

class LogCorruptionError(Exception):
    """Raised when a log has corrupted data."""
    pass


def store_message(topic, encoded_message):
    path = os.path.join("logs", topic + ".log")
    os.makedirs("logs", exist_ok=True)
    checksum = zlib.crc32(encoded_message)
    crc_prefix = checksum.to_bytes(CHECKSUM_SIZE, 'big')
    crc_message = crc_prefix + encoded_message
    with open(path, "ab") as f:
        f.write(crc_message)
        f.flush()
        os.fsync(f.fileno())

def scan(path):
    if os.path.exists(path):
        file_size = os.path.getsize(path)
        pos = 0
        with open(path, "rb") as f:
            data = f.read()
            while True:
                checksum_read = data[pos:pos + CHECKSUM_SIZE]
                checksum_length = len(checksum_read)
                if checksum_length == 0:
                    print("Checksum length was 0")
                    return (pos, CLEAN_END)
                if checksum_length != CHECKSUM_SIZE:
                    print("Incomplete checksum")
                    return (pos, TORN_TAIL)
                checksum = int.from_bytes(checksum_read, "big")
                length_read = data[pos + CHECKSUM_SIZE:pos + CHECKSUM_SIZE + LENGTH_SIZE]
                N = int.from_bytes(length_read, "big")
                if len(length_read) < LENGTH_SIZE:
                    print("Incomplete prefix")
                    return (pos, TORN_TAIL)
                entry_end = pos + CHECKSUM_SIZE + LENGTH_SIZE + N
                if entry_end > file_size:
                    print("Entry runs past EOF")
                    return (pos, TORN_TAIL)
                else:
                    body_read = data[pos + CHECKSUM_SIZE + LENGTH_SIZE:pos + N + CHECKSUM_SIZE + LENGTH_SIZE]
                    if len(body_read) < N:
                        print("Short read")
                        return (pos, TORN_TAIL)
                    body_checksum = zlib.crc32(length_read+body_read)
                    if checksum != body_checksum:
                        if entry_end == file_size:
                            print("Invalid checksum")
                            return (pos,TORN_TAIL)
                        else:
                            print("Checksum mismatch")
                            return (pos, CORRUPTION)
                pos = entry_end
    else:
        print("Path not found")
        return (0, CLEAN_END)

def recover(path):
    position, category = scan(path)
    if category == TORN_TAIL:
        os.truncate(path, position)
        return position
    elif category == CORRUPTION:
        raise LogCorruptionError(f"Corrupted data on file: {path}, position: {position}")
    else:
        return position



store_message("news", encode_message({"payload": "hi"}))
store_message("news", encode_message({"payload": "bye"}))