import asyncio
from broker.protocol import encode_message, read_length, read_message
import time

async def test_function():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Connected")
    topic = "test-topic"
    timestamp = time.time()
    payload = input("Type your message: ")
    message = {"topic":topic, "timestamp":timestamp, "payload":payload}
    encoded_message = encode_message(message)
    writer.write(encoded_message)
    print("Sent")
    await writer.drain()
    length = await read_length(reader)
    data = await read_message(reader,length)
    print(data)

asyncio.run(test_function())