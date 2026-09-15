import asyncio
import json
 
def encode_message(data_dict):
    data = json.dumps(data_dict)
    encoded = data.encode()
    length_data = len(encoded)
    length_prefix = length_data.to_bytes(4, 'big')
    return length_prefix + encoded

async def read_length(reader):
    length_bytes = await reader.read(4)
    return int.from_bytes(length_bytes, 'big')

async def read_message(reader,length):
    data = await reader.read(length)
    data_string = data.decode()
    return json.loads(data_string)
