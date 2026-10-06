import os
from broker.protocol import encode_message

def store_message(topic, encoded_message):
    path = os.path.join("logs", topic + ".log")
    os.makedirs("logs", exist_ok=True)
    with open(path, "ab") as f:
        f.write(encoded_message)
        f.flush()
        os.fsync(f.fileno())

store_message("news", encode_message({"payload": "hi"}))
store_message("news", encode_message({"payload": "bye"}))