from secrets import secrets

def connect_wifi():
	try:
		import wifi
		native_wifi = True
	except:
		native_wifi = False
	
	if native_wifi:
		#import wifi
		import socketpool
		import ssl

		print("CONNECT WIFI")
		wifi.radio.connect(secrets['ssid'],secrets['password'])
		socket = socketpool.SocketPool(wifi.radio)
		ssl_context = ssl.create_default_context()
		return (socket, ssl_context, None)
	
	else:
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
		return (socket, None, esp)
	
	return (None, None, None)
