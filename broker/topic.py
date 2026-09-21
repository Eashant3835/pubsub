from protocol import encode_message

class TopicManager:
    def __init__(self):
        self.topics = {}
        self.writers = {}

    def subscribe(self, topic, writer):
        if topic not in self.topics:
            self.topics[topic] = []
        if writer not in self.writers:
            self.writers[writer] = []
        self.topics[topic].append(writer)
        self.writers[writer].append(topic)

    async def publish(self, topic, message):
        if topic not in self.topics or not self.topics[topic]:
            return None
        encoded_message = encode_message(message)
        for writer in self.topics[topic]:
            writer.write(encoded_message)
            await writer.drain()

    def disconnect(self,writer):
        if writer not in self.writers or not self.writers[writer]:
            return None
        for topic in self.writers[writer]:
            self.topics[topic].remove(writer)
        self.writers.pop(writer,None)

