from broker.protocol import encode_message
from broker.log import store_message

class TopicManager: 

    async def publish(self, topic, payload):
        encoded_message = encode_message(payload)
        store_message(topic,encoded_message)
