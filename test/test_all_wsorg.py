# set debug to False for future imports
#import micropython
#micropython.opt_level(1)

import time
import sys
import json
from secrets import secrets

#####################################################################

try:
	import wifi
	import socketpool
	import ssl

	print("CONNECT WIFI")
	wifi.radio.connect(secrets['ssid'],secrets['password'])
	socket = socketpool.SocketPool(wifi.radio)
	ssl_context = ssl.create_default_context()
	iface = None

except:
	import board
	import busio
	from digitalio import DigitalInOut
	from adafruit_esp32spi import adafruit_esp32spi
	
	esp32_cs = DigitalInOut(board.D13)
	esp32_ready = DigitalInOut(board.D11)
	esp32_reset = DigitalInOut(board.D12)
	
	spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
	esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
	
	print("CONNECT WIFI")
	while not esp.is_connected:
		try:
			esp.connect_AP(secrets["ssid"], secrets["password"])
		except RuntimeError as e:
			print("could not connect to AP, retrying: ", e)
			continue
	
	import adafruit_esp32spi.adafruit_esp32spi_socket as socket
	socket.set_interface(esp)
	ssl_context = None
	iface = esp

#####################################################################

import uwebsockets.client
from uwebsockets.socket import UniversalSocket
uSocket = UniversalSocket(socket, ssl = ssl_context, iface = iface)

message = "Repeat this"
urls = [
	"wss://echo.websocket.org",
	"ws://echo.websocket.org",
]
#"ws://spyromini.local:5000"

for url in urls:
	print(f"TESTING ECHO {url}")
	with uwebsockets.client.connect(url,uSocket) as ws:
		print(f"SENDING:  <{message}>")
		ws.send(message)
		result = ws.recv()
		print(f"RECEIVED: <{result}>")
		if result == message:
			print("SUCCESS !!")
		else:
			print("OH NO IT WENT WRONG")
