import asyncio
from broker.protocol import encode_message, read_length, read_message
from broker.topic import TopicManager
from broker.log import load_indexes, indexes, store_position
import re
from broker.log import read_entry, load_positions, POSITIONS_PATH
import os
import json

class Broker:
    def __init__(self, manager):
        self.manager = manager
        self.positions = {} 

    async def handle_client(self,reader,writer):
        manager = self.manager
        try:
            while True:
                try:
                    length = await read_length(reader)
                    data = await read_message(reader,length)
                except asyncio.IncompleteReadError:
                    print("Disconnected")
                    break

                topic = data["topic"]
                try:
                    pattern = r"[a-zA-Z0-9_-]+"
                    if not re.fullmatch(pattern, topic):
                        raise ValueError()
                except ValueError:
                    print("Please only use number, letters or '-' and '_' for topic names.")
                    break
                
                print(f"Recieved: {data}")

                if data["type"] == "publish":
                    await manager.publish(topic, data["payload"])
                    ack = {"type": "PublishAck", "topic": topic, "id": data["id"]}
                    writer.write(encode_message(ack))
                    await writer.drain()

                elif data["type"] == "fetch":
                    consumer_id = data["consumer_id"]
                    last = self.positions.get((consumer_id,topic),-1)
                    offset = last + 1
                    path = os.path.join("logs", topic + ".log")
                    body = read_entry(path, indexes.get(topic, []), offset)
                    if body is None:
                        reply = {"type": "NothingYet", "topic": topic}
                        writer.write(encode_message(reply))
                        await writer.drain()
                    else:
                        reply = {"type": "FetchReply", "topic": topic, "offset": offset, "payload": json.loads(body)}
                        writer.write(encode_message(reply))
                        await writer.drain()

                elif data["type"] == "commit":
                    store_position(data["consumer_id"], topic, data["offset"])
                    self.positions[(data["consumer_id"], topic)] = data["offset"] 
                
                else:
                    print("Data type error")
        finally:
            writer.close()  

async def main():
    manager = TopicManager()
    broker = Broker(manager)
    broker.positions = load_positions(POSITIONS_PATH)
    load_indexes("logs")
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()
if __name__ == "__main__":
    asyncio.run(main())