import asyncio
import time
from broker.protocol import encode_message

class Producer:
    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        print("Producer Connected!")

    async def publish(self,topic,payload):
        timestamp = time.time()
        message = {"topic":topic, "timestamp":timestamp, "payload":payload, "type":"publish"}
        encoded_message = encode_message(message)
        self.writer.write(encoded_message)
        print("Sent")
        await self.writer.drain()