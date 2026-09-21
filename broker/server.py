import asyncio
from protocol import encode_message, read_length, read_message
from topic import TopicManager
class Broker:
    def __init__(self, manager):
        self.manager = manager

    async def handle_client(self,reader,writer):
        manager = self.manager
        while True:
            length = await read_length(reader)
            if length == 0:
                manager.disconnect(writer)
                print("Disconnected")
                break
            data = await read_message(reader,length)
            topic = data["topic"]
            print(f"Recieved: {data}")

            if data["type"] == "publish":
                message = data["payload"]
                await manager.publish(topic,message)

            elif data["type"] == "subscribe":
                manager.subscribe(topic,writer)
                print("Subscribed!")

            else:
                print("Data type error")

async def main():
    manager = TopicManager()
    broker = Broker(manager)
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())