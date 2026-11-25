import asyncio, os
from broker.server import Broker
from broker.topic import TopicManager
from broker.log import load_indexes, POSITIONS_PATH
from client.producer import Producer

topic = "acktest"
sent_id = "abc"
path = os.path.join("logs", topic + ".log")
if os.path.exists(path):
    os.remove(path)

async def main():
    broker = Broker(TopicManager())
    load_indexes("logs")
    server = await asyncio.start_server(broker.handle_client, '127.0.0.1', 8888)
    async with server:
        producer = Producer()
        await producer.connect()
        ack = await  producer.publish(topic, "HI", id=sent_id)      # publish now returns the reply
        print(ack)
        assert  ack>["type"] == "PublishAck"
        assert  ack>["topic"] == topic
        assert  ack>["id"] ==  sent_id
        producer.writer.close()

asyncio.run(main())
os.remove(path)