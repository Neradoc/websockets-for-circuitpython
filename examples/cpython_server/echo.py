# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
# SPDX-License-Identifier: MIT

import asyncio
import logging
import os
import socket
import websockets


logging.basicConfig(
    format="%(message)s",
    level=logging.DEBUG,
)


PORT = 5000
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname)

print(f"Access: {HOST}:{PORT}")


async def echo(websocket, path):
    try:
        async for message in websocket:
            print("Received and echoing message: " + message, flush=True)
            await websocket.send(message)
    except:
        print("Bye")


start_server = websockets.serve(echo, "0.0.0.0", PORT)

print("WebSockets echo server starting", flush=True)
asyncio.get_event_loop().run_until_complete(start_server)

print("WebSockets echo server running", flush=True)
asyncio.get_event_loop().run_forever()
