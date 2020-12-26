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

ws.send("Rock it with HTML5 WebSocket")
result = ws.recv()
print("RESULT",result)
