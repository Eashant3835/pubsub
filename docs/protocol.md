# Pub/Sub Protocol Specifications
The wire protocol: message formats and how frames are sent and received.

# Spec:

## Definitions:

### Frame: A 4-byte unsigned big-endian length prefix, followed by the body. The prefix holds the number of bytes in the body.

### Body: The bytes following the length prefix, which are UTF-8 text of JSON

### Message: a JSON object with the fields type, topic, timestamp and payload, sent by the client to the broker

### A disconnect is when the receiver stops reading and closes its end, and the broker also removes that client’s subscriptions. 

## Sender:

1) The sender starts with a JSON value. For a client it's a message, for a broker delivering the message it's the payload value alone.

2) The JSON value is serialized into JSON text.

3) The JSON text is encoded into UTF-8 bytes, the result being the body.

4) The number of bytes in the body is counted and then written as the length prefix.

5) The sender writes the frame: The prefix then the body.

## Receiver:

The broker and consumer follow these steps:

1) The receiver reads the 4 byte prefix.

2) The 4 bytes are interpreted as the number N.

3) Exactly N bytes (the body) are read from the byte stream.

4) The receiver decodes N bytes of the body as UTF-8 to get JSON text.

5) The receiver parses the text as JSON to get the value

## Rules: 
Length of 0: The receiver closes the connection and sends no error reply.

Stream ends before the full prefix or body arrives or streams that end cleanly between frames: The receiver closes the connection.

A body that isn't valid UTF-8 or isn’t valid JSON: The receiver closes the connection and sends no error reply.

## Direction
Client -> Broker: Body decodes to a JSON object with type, topic, timestamp, and payload
Broker -> Consumer: Body decodes to the payload value on its own. It can be any JSON value

# Message keys:
# type
### Type:
JSON String
### Required:
Yes, for all messages
### Meaning:
Used to distinguish the purpose of the message
### Rules:

### Allowed values:
"subscribe"(Sent by the consumer when subscribing to a topic. Repeat subscribes are ignored, broker subscribes the consumer to the topic), "publish"(Sent by the producer when sending a message, broker processes, stores (it stores even if the topic has no consumers) and delivers the payload to the consumers of the topic)

### Matching:
exact, case sensitive

### Unrecognized value (including empty):
The message is ignored, the connection stays open and the client is not told

### Key missing:
The broker closes the connection and the client is not told

# topic

### Type: 
JSON String

### Required: 
Yes, for all messages

### Meaning: 
The topic the message is about

## Rules:

### Allowed values: 
Any JSON string that is one or more characters, each an ASCII letter, a digit, '-' or '_'.

### Matching: 
exact, case sensitive ("ABC" is a different topic from "abc")

### Invalid value: 
The connection is closed and the client isn't told. This is checked before the type so a message with a bad topic and an unknown type still closes the connection.

### Missing key:  
The connection is closed and the client isn't told.

# timestamp

### Type: 
JSON Number, may have a fractional part.

### Required: 
No,the client library always sends it so a message built by the producer or consumer includes it even though it is not required.

### Meaning: 
What time the message was built by the client, seconds since the Unix epoch (1970-01-01 00:00 UTC). It's the client's clock and is not verified by the broker so it can be wrong or out of sync

## Rules: 

### Valid value: 
Accepted and ignored.

### Missing key: 
Accepted and ignored.

### Invalid Value(anything that's not a number): 
Accepted and ignored.

# payload

### Type: 
Any JSON value(string, number, boolean, null, array, object), the type isn't checked.

### Required: 
Yes, only for "publish" messages though.

### Meaning: 
The content that needs to be delivered. A consumer's frame body decodes to the payload value itself.

## Rules:
### subscribe:
The client library’s subscribe sends a payload anyway, and the broker ignores it for subscribe.

## publish:

### Empty Values ("", 0, false, null): 
Accepted and delivered unchanged.

### Missing key: 
The connection is closed and the client isn’t told. Nothing is stored in the log.

### Size limit:
The size limit is about 4GB.

### Delivery:
Every subscriber of the topic receives the same JSON value.

# Message types:

## Publish

### Sent by: 
Producer

### Fields: 
type, topic and payload are required while timestamp is ignored.

### Broker does: 
The payload is extracted and stored. The broker then sends the payload to the consumers of the topic. Each consumer gets a frame whose body decodes to the payload value. If the topic has no subscribers, the payload is still stored and nothing is delivered.

## Subscribe

### Sent by: 
Consumer
### Fields: 
type and topic are required, while timestamp and payload are ignored.

### Broker does: 
The broker adds the connection as a subscriber to the topic. If the topic does not exist, a new one is created. A repeat subscribe is ignored. The subscription lasts until the connection closes, and there’s no unsubscribe message. 

## Behavior common to both types:

### Replies:
The broker sends no reply to either message type, so the sender can't tell whether a request succeeded. Acknowledgements are a limitation as of now but are planned to be added. 

### Ordering:
Messages from a single producer reach each subscriber in the order they were sent. No ordering is guaranteed between messages from different producers. Different subscribers might see the messages in different orders.

### Bad input:
In the case of an invalid topic value (using characters other than ASCII letters, digits, ‘-’, ‘_’), an empty topic, a missing topic or type key, the connection is closed and the client is not told. In the case of an unrecognized message type, the connection stays open, the message is ignored and the client is not told.

# RELEVANT LIMITATIONS:
## No acknowledgements
## No ordering across different producers
## No explanations for rejected clients