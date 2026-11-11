import os
from broker.protocol import encode_message
import zlib

CHECKSUM_SIZE = 4
LENGTH_SIZE = 4
CLEAN_END = "clean end"
TORN_TAIL = "torn tail"
CORRUPTION = "corruption"

indexes = {}

class LogCorruptionError(Exception):
    """Raised when a log has corrupted data."""
    pass


def store_message(topic, encoded_message):
    path = os.path.join("logs", topic + ".log")
    os.makedirs("logs", exist_ok=True)
    checksum = zlib.crc32(encoded_message)
    crc_prefix = checksum.to_bytes(CHECKSUM_SIZE, 'big')
    crc_message = crc_prefix + encoded_message
    start = os.path.getsize(path) if os.path.exists(path) else 0
    with open(path, "ab") as f:
        f.write(crc_message)
        f.flush()
        os.fsync(f.fileno())
    indexes.setdefault(topic, []).append(start)
    return (len(indexes[topic]) - 1)

def scan(path):
    if os.path.exists(path):
        file_size = os.path.getsize(path)
        pos = 0
        starts = []
        with open(path, "rb") as f:
            data = f.read()
            while True:
                checksum_read = data[pos:pos + CHECKSUM_SIZE]
                checksum_length = len(checksum_read)
                if checksum_length == 0:
                    print("Checksum length was 0")
                    return (pos, CLEAN_END, starts)
                if checksum_length != CHECKSUM_SIZE:
                    print("Incomplete checksum")
                    return (pos, TORN_TAIL, starts)
                checksum = int.from_bytes(checksum_read, "big")
                length_read = data[pos + CHECKSUM_SIZE:pos + CHECKSUM_SIZE + LENGTH_SIZE]
                N = int.from_bytes(length_read, "big")
                if len(length_read) < LENGTH_SIZE:
                    print("Incomplete prefix")
                    return (pos, TORN_TAIL, starts)
                entry_end = pos + CHECKSUM_SIZE + LENGTH_SIZE + N
                if entry_end > file_size:
                    print("Entry runs past EOF")
                    return (pos, TORN_TAIL, starts)
                else:
                    body_read = data[pos + CHECKSUM_SIZE + LENGTH_SIZE:pos + N + CHECKSUM_SIZE + LENGTH_SIZE]
                    if len(body_read) < N:
                        print("Short read")
                        return (pos, TORN_TAIL, starts)
                    body_checksum = zlib.crc32(length_read+body_read)
                    if checksum != body_checksum:
                        if entry_end == file_size:
                            print("Invalid checksum")
                            return (pos, TORN_TAIL, starts)
                        else:
                            print("Checksum mismatch")
                            return (pos, CORRUPTION, starts)
                starts.append(pos)
                pos = entry_end
    else:
        print("Path not found")
        return (0, CLEAN_END, [])

def recover(path):
    position, category, starts = scan(path)
    if category == TORN_TAIL:
        os.truncate(path, position)
        return position, starts
    elif category == CORRUPTION:
        raise LogCorruptionError(f"Corrupted data on file: {path}, position: {position}")
    else:
        return position, starts

def load_indexes(logs_dir):
    os.makedirs("logs", exist_ok=True)
    for filename in os.listdir(logs_dir):
        if not filename.endswith(".log"):
            continue
        topic = filename.removesuffix(".log")
        path = os.path.join(logs_dir,filename) 
        position,starts = recover(path)
        indexes[topic] = starts

def read_entry(path, starts, offset):
    if offset < 0:
        raise ValueError(offset)
    if offset >= len(starts):
        return None
    with open(path, "rb") as f:
        f.seek(starts[offset])
        position = starts[offset]
        header = f.read(CHECKSUM_SIZE+LENGTH_SIZE)
        if len(header) < CHECKSUM_SIZE + LENGTH_SIZE:
            raise LogCorruptionError(f"Corrupted data on file: {path}, position: {position}")
        checksum_bytes = header[:CHECKSUM_SIZE]
        checksum = int.from_bytes(checksum_bytes,"big")
        length_bytes = header[CHECKSUM_SIZE:]
        length = int.from_bytes(length_bytes,"big")
        body = f.read(length)
        if len(body) < length:
            raise LogCorruptionError(f"Corrupted data on file: {path}, position: {position}")
        check = zlib.crc32(length_bytes + body)
        if check != checksum:
            raise LogCorruptionError(f"Corrupted data on file: {path}, position: {position}")
        return body


if __name__ == "__main__":
    store_message("news", encode_message({"payload": "hi"}))
    store_message("news", encode_message({"payload": "bye"}))