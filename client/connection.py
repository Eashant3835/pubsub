import asyncio
from producer import Producer
from consumer import Consumer

async def consumer_test():
    consumer = Consumer()
    await consumer.connect()
    await consumer.subscribe("test-topic")
    message = await consumer.recieve()
    print(message)

async def producer_test():
    producer = Producer()
    await producer.connect()
    await producer.publish("test-topic","test")

async def main():
    await asyncio.gather(consumer_test(),producer_test())

asyncio.run(main())