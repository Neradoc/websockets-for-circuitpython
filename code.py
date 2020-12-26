import time
import sys
import json

import wifi
import socketpool
import ssl
import secrets

wifi.radio.connect(secrets.ssid,secrets.password)
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()

print("connected with SSL ready ?")

import uwebsockets.client

url = "wss://echo.websocket.org"
ws = uwebsockets.client.connect(url)

message = "Repeat this"
ws.send(message)
result = ws.recv()
print("RESULT",result)
if result == message:
	print("SUCCESS")
