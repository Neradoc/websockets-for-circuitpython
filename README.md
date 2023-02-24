# Websockets For Circuitpython
My tests with uwebsockets on circuitpython before maybe making a genuine fork/port.

The code has been adpated to the ESP32S2 firt, then back to using socket.recv and such. It is not currently based on the latest uwebsockets, but an older version that I was using and worked with my code. *Don't forget to fill in the wifi SSID and password in secrets.py*.

### Universal Sockets branch for ESP32S2 and Airlift
-	Create a `websockets.Session` with:
	-	**socket** the socket module.
	-	**ssl=** the `ssl_context` for S2 (optional).
	-	**iface=** the `ESP_SPIcontrol` interface object (optional).
-	`with session.client(url) as ws`
	-	Connect as a client and return the WebSockets object.
	-	Url is `ws://server:port` or `wss://server:port`
	-	Use `ws.send` and `ws.recv` to exchange data with the server.
-	Uses a UniversalSocket abstraction class to encapsulate the differences.
	-	`uwebsockets` client and protocol are left as unchanged as possible.
	-	*(For now)*

-	Tested on FeatherS2.
-	Tested on nrf52840 Feather + Airflit Featherwing.

Original uwebsockets implementation:
https://github.com/danni/uwebsockets


SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
SPDX-License-Identifier: MIT
