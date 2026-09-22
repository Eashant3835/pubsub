import asyncio
from producer import Producer
from consumer import Consumer

async def consumer_test():
    consumer = Consumer()
    await consumer.connect()
    await consumer.subscribe("test-topic")
    message = await consumer.recieve()
    print(message)

async def consumer_test2():
    consumer2 = Consumer()
    await consumer2.connect()
    await consumer2.subscribe("test-topic")
    message = await consumer2.recieve()
    print(message)

async def consumer_test3():
    consumer3 = Consumer()
    await consumer3.connect()
    await consumer3.subscribe("test-topic")
    message = await consumer3.recieve()
    print(message)

async def producer_test():
    producer = Producer()
    await producer.connect()
    await producer.publish("test-topic","test")
    await producer.publish("test-topic","test")
    await producer.publish("test-topic","test")
    

async def main():
    await asyncio.gather(consumer_test(),consumer_test2(),consumer_test3(),producer_test())

asyncio.run(main())