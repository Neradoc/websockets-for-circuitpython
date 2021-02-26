## set debug to False for future imports (removes logging)
import micropython
micropython.opt_level(1)

import json
import sys
import time

from secrets import secrets
from status_led import status_led
from connect_circuitpython import connect_wifi
from uwebsockets import Session

socket, ssl_context, iface = connect_wifi()
wsession = Session(socket, ssl = ssl_context, iface = iface)

message = "Repeat this"
url = "ws://{}:{}".format(secrets['test_server'], secrets['test_port'])

print(f"Connecting to {url}")
with wsession.client(url) as ws:
	print("START")
	ws.send("START")
	ws.settimeout(0.5)
	while True:
		try:
			result = ws.recv()
		except Exception as ex:
			if ex.args[0] == 116:
				result = None
			else:
				raise
	
		if result != None:
			try:
				data = json.loads(result)
			except:
				data = {}
			if 'color' in data:
				try:
					color = data['color']
					print(f"Color: {color}")
					status_led[0] = color
				except:
					print(f"ERREUR de couleur {data['color']}")
			if 'response' in data:
				print("<",data['response'])

		time.sleep(0.1)
