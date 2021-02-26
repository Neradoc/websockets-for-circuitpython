import asyncio
import json
import re
import time
import websockets


async def consumer(message):
	print(message)


async def producer():
	color = input("Color:")
	if re.match('^\d+$',color):
		color = int(color)
	elif re.match('^\((\d+),(\d+),(\d+)\)$',color):
		m = re.match('^\((\d+),(\d+),(\d+)\)$',color)
		color = (int(m.group(1)),int(m.group(2)),int(m.group(3)))
	elif re.match('^\[(\d+),(\d+),(\d+)\]$',color):
		m = re.match('^\[(\d+),(\d+),(\d+)\]$',color)
		color = (int(m.group(1)),int(m.group(2)),int(m.group(3)))
	elif re.match('^0x([a-fA-F0-9]+)$',color):
		m = re.match('^0x([a-fA-F0-9]+)$',color)
		color = int(m.group(1),16)
	return json.dumps({"color":color})


async def consumer_handler(websocket, path):
	async for message in websocket:
		await consumer(message)


async def producer_handler(websocket, path):
	while True:
		message = await producer()
		print(">",message)
		await websocket.send(message)


async def handler(websocket, path):
	consumer_task = asyncio.ensure_future(
		consumer_handler(websocket, path))
	producer_task = asyncio.ensure_future(
		producer_handler(websocket, path))
	done, pending = await asyncio.wait(
		[consumer_task, producer_task],
		return_when=asyncio.FIRST_COMPLETED,
	)
	for task in pending:
		task.cancel()


print("Starting")
start_server = websockets.serve(handler, '0.0.0.0', 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

