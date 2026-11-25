import asyncio, os
from broker.server import Broker
from broker.topic import TopicManager
from broker.log import load_indexes, POSITIONS_PATH
from client.producer import Producer
from client.consumer import Consumer

topic = "emptytest"
path = os.path.join("logs", topic + ".log")
if os.path.exists(path):
    os.remove(path)

async def main():
    broker = Broker(TopicManager())
    load_indexes("logs")
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        consumer = Consumer()
        await consumer.connect()

        reply1 = await consumer.fetch(topic, "def")
        assert reply1["type"] == "NothingYet" and reply1["topic"] == topic

        producer = Producer()
        await producer.connect()
        await producer.publish(topic, "HI")
        reply2 = await consumer.fetch(topic, "def")
        assert reply2["type"] == "FetchReply"
        await consumer.commit(topic, "def", reply2["offset"])
        await asyncio.sleep(0.5)
        reply3 = await consumer.fetch(topic, "def")
        assert reply3["type"] == "NothingYet"
        producer.writer.close()
        consumer.writer.close()

asyncio.run(main())
os.remove(path)
if os.path.exists(POSITIONS_PATH):
    os.remove(POSITIONS_PATH)