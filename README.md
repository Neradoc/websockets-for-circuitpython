# websockets-circuitpython-test
My tests with uwebsockets on circuitpython before maybe making a genuine fork/port.

The code has been adpated to the ESP32S2 firt, then back to using socket.recv and such. It is not currently based on the latest uwebsockets, but an older version that I was using and worked with my code. *Don't forget to fill in the wifi SSID and password in secrets.py*.

### Universal Sockets branch works with ESP32S2 and Airlift
-	create a `websockets.Session` with the socket module and:
	-	**ssl=** the `ssl_context` for S2
	-	**iface=** the `ESP_SPIcontrol` interface object
-	uses the UniversalSocket abstraction class to encapsulate the differences
	-	uwebsockets client and protocol are left as unchanged as possible

### ESP32S2 branch works with native wifi on the ESP32S2
-	tested successfully on FeatherS2

### Airlift version works with SPI ESP32 module
-	tested successfully on nrf52840 Feather + Airflit Featherwing

Original repository:
https://github.com/danni/uwebsockets
