import asyncio
from broker.protocol import encode_message, read_length, read_message
import time

class Consumer:
    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        print("Consumer Connected!")

    async def subscribe(self,topic):
        timestamp = time.time()
        message = {"topic":topic, "timestamp":timestamp, "payload":"Subscribed!", "type":"subscribe"}
        encoded_message = encode_message(message)
        self.writer.write(encoded_message)
        await self.writer.drain()

    async def recieve(self):
        length = await read_length(self.reader)
        data = await read_message(self.reader,length)
        return(data)
    
    async def fetch(self, topic, consumer_id):
        message = {"type": "fetch", "topic": topic, "consumer_id": consumer_id}
        self.writer.write(encode_message(message))
        await self.writer.drain()
        return await self.recieve()

    async def commit(self, topic, consumer_id, offset):
        message = {"type": "commit", "topic": topic, "consumer_id": consumer_id, "offset": offset}
        self.writer.write(encode_message(message))
        await self.writer.drain()