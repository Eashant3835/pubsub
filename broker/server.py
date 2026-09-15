import asyncio
from protocol import encode_message, read_length, read_message

async def handle_client(reader,writer):
   while True:
    length = await read_length(reader)
    if length == 0:
        print("Disconnected")
        break
    data = await read_message(reader,length) 
    print(f"Recieved: {data}")
    message = encode_message(data)
    writer.write(message)
    await writer.drain() #What is drain? When sending messages to a server, it sends to a temporary area first, drain basically makes sure the messages dont pile up in that area

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

asyncio.run(main())