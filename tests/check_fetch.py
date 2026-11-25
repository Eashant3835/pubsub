import asyncio, os
from broker.server import Broker
from broker.topic import TopicManager
from broker.log import load_indexes, POSITIONS_PATH, load_positions
from client.producer import Producer
from client.consumer import Consumer

topic = "wow"
path = os.path.join("logs", topic + ".log")
if os.path.exists(path):
    os.remove(path)

async def main():
    manager = TopicManager()
    broker = Broker(manager)
    load_indexes("logs")
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        producer = Producer()
        await producer.connect()
        await producer.publish(topic, "HI")
        await producer.publish(topic, "BYE")
        await asyncio.sleep(0.5)
        consumer = Consumer()
        await consumer.connect()
        reply = await consumer.fetch(topic, "1234")
        print(reply)
        await consumer.commit(topic, "1234", reply["offset"])
        await asyncio.sleep(0.5)
        reply2 = await consumer.fetch(topic, "1234")
        print(reply2)
        await consumer.commit(topic, "1234", reply2["offset"])
        assert reply["offset"] == 0 and reply["payload"] == "HI"
        assert reply2["offset"] == 1 and reply2["payload"] == "BYE"
        producer.writer.close()
        consumer.writer.close()
        print(load_positions(POSITIONS_PATH))
asyncio.run(main())
os.remove(path)
