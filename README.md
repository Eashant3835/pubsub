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