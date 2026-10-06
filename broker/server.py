import asyncio
from broker.protocol import encode_message, read_length, read_message
from broker.topic import TopicManager
import re

class Broker:
    def __init__(self, manager):
        self.manager = manager

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
                    message = data["payload"]
                    await manager.publish(topic,message)

                elif data["type"] == "subscribe":
                    manager.subscribe(topic,writer)
                    print("Subscribed!")

                else:
                    print("Data type error")
        finally:
            manager.disconnect(writer)
async def main():
    manager = TopicManager()
    broker = Broker(manager)
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()
if __name__ == "__main__":
    asyncio.run(main())