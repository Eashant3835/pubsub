import asyncio
import time
from broker.protocol import encode_message, read_length, read_message
import uuid


class Producer:
    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        print("Producer Connected!")

    async def publish(self,topic,payload, id=None):
        timestamp = time.time()
        message = {"topic": topic, "timestamp": timestamp, "payload": payload, "type": "publish", "id": id or uuid.uuid4().hex}
        encoded_message = encode_message(message)
        self.writer.write(encoded_message)
        print("Sent")
        await self.writer.drain()
        length = await read_length(self.reader)
        return await read_message(self.reader, length)