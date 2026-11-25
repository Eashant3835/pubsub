from broker.log import POSITIONS_PATH, load_indexes, load_positions
import os
from broker.topic import TopicManager
from broker.server import Broker
import asyncio
from client.producer import Producer
from client.consumer import Consumer
import traceback

topic = "wow"
path = os.path.join("logs", topic + ".log")
for p in (path, POSITIONS_PATH):
    if os.path.exists(p):
        os.remove(p)

async def main():
    manager1 = TopicManager()
    broker1 = Broker(manager1)
    load_indexes("logs")
    server1 =  await asyncio.start_server(broker1.handle_client, '127.0.0.1', 8888)
    async with server1:
        producer1 = Producer()
        consumer1 = Consumer()
        await producer1.connect()
        await producer1.publish(topic, "HI")
        await producer1.publish(topic, "BYE")
        await asyncio.sleep(0.5)
        await consumer1.connect()
        reply = await consumer1.fetch(topic, "1234")
        await consumer1.commit(topic, "1234", reply["offset"])
        await asyncio.sleep(0.5)
        producer1.writer.close()
        consumer1.writer.close()
        print("phase 1 done")
        broker2 = Broker(TopicManager())
        print("loading positions")
        broker2.positions = load_positions(POSITIONS_PATH)
        print("positions loaded:", broker2.positions)
    print("server1 closed")
    server2 = await asyncio.start_server(broker2.handle_client, '127.0.0.1', 8888)
    print("server2 started")
    async with server2:
        consumer2 = Consumer()
        await consumer2.connect()
        print("fetching")
        reply3 = await consumer2.fetch(topic, "1234")
        print("got:", reply3)
        assert reply3["offset"] == 1 and reply3["payload"] == "BYE"
        consumer2.writer.close()

try:
    asyncio.run(main())
except BaseException:
    traceback.print_exc()