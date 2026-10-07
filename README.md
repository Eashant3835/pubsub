# pub/sub

This project is a pub/sub message broker built from scratch in Python. It's inspired by Kafka and it exists as a learning project to understand the internal mechanics of pub/sub. It currently supports TCP server connections, multi subscriber fan outs, framing TCP messages over a byte stream and topic based routing. Features like persistence, at least once delivery and idempotency are planned to be added.

## Quickstart

### Step 1
Clone the repo using

```
git clone https://github.com/Eashant3835/pubsub.git
```

and cd into it using

```
cd pubsub
```

### Step 2
Requires Python (developed on Python 3.14). No dependencies to install.

### Step 3
From the repo level folder (the one containing broker/ and client/) run 

```
python3 -m broker.server
```
The terminal will appear to hang. That's expected, since the broker is waiting for connections. Press Ctrl+C to stop it when you're done.

### Step 4
In a second terminal, from the same folder run

```
python3 -m client.connection
```

### Step 5
The expected output should look like:
```
Consumer Connected!
Consumer Connected!
Consumer Connected!
Producer Connected!
Sent
Sent
test1
test1
test2
```
Three consumers connect, two subscribe to the same topic and one to a different topic, the producer publishes once to each topic, and the shared topic's message shows up twice (once per consumer).

## Limitations:

Nothing is acknowledged.

A malformed message crashes that client’s handler.

A subscriber dying mid-publish can break the publisher.

Empty topics are never pruned.

A consumer gets an unhandled exception if the broker closes its connection.

Consumers only receive the payload with no topic.

os.fsync is a blocking call so it while its fsyncing it cant do anything else.

A rejected client gets no explanation, because there's no reply channel until acks exist.

Topics are validated on the broker but not the client.

Length 0 is invalid but not enforced yet.

The log only keeps the payload.

A crash mid append can leave a partial entry.

Logs grow without limit.

The log directory is relative to where the broker is launched. Starting it from a different folder creates a second logs/.
