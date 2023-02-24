from aioconsole import ainput
import asyncio
import json
import re
import time
import sys
import websockets


color_names = {
    "aqua": 0x00FFFF,
    "black": 0x000000,
    "blue": 0x0000FF,
    "green": 0x008000,
    "magenta": 0xFF00FF,
    "orange": 0xFFA500,
    "pink": 0xF02080,
    "purple": 0x800080,
    "red": 0xFF0000,
    "turquoise": 0x40E0D0,
    "white": 0xFFFFFF,
    "yellow": 0xFFFF00,
}

COLOR_PROMPT = "Color >>> "


async def consumer(message):
    try:
        data = json.loads(message)
    except:
        data = {}
    try:
        if "buttons" in data:
            for button, action in data["buttons"].items():
                if action == "released":
                    print("")
                    print(f"Button clicked: {button}")
                    print(COLOR_PROMPT, end="")
                    sys.stdout.flush()
    except:
        print("Malformed buttons", data)


async def producer():
    color = await ainput(COLOR_PROMPT)
    color = color.strip()
    if color == "":
        return None
    elif re.match("^\d+$", color):
        color = int(color)
    elif re.match("^\((\d+),(\d+),(\d+)\)$", color):
        m = re.match("^\((\d+),(\d+),(\d+)\)$", color)
        color = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    elif re.match("^\[(\d+),(\d+),(\d+)\]$", color):
        m = re.match("^\[(\d+),(\d+),(\d+)\]$", color)
        color = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    elif re.match("^0x([a-fA-F0-9]+)$", color):
        m = re.match("^0x([a-fA-F0-9]+)$", color)
        color = int(m.group(1), 16)
    elif color.lower() in color_names:
        color = color_names[color.lower()]
    return json.dumps({"color": color})


async def consumer_handler(websocket, path):
    print(f"START consumer_handler {path}")
    async for message in websocket:
        # print("<", message)
        await consumer(message)


async def producer_handler(websocket, path):
    print(f"START producer_handler {path}")
    while True:
        message = await producer()
        if message:
            # print(">", message)
            await websocket.send(message)


async def handler(websocket, path):
    print("Connection from {}".format(websocket.remote_address))
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


print("Starting")
start_server = websockets.serve(handler, "0.0.0.0", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
