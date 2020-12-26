# websockets-circuitpython-test
My tests with uwebsockets on circuitpython before maybe making a genuine fork/port.

The code has been adpated to the ESP32S2 firt, then back to using socket.recv and such. It is not currently based on the latest uwebsockets, but an older version that I was using and worked with my code.

Making full port will require:
- abstracting the differences between the two ports (look at adafruit_requests)
- update to match the latest uwebsockets
- cleanup prints and probably remove logging

ESP32S2 branch works with native wifi on the ESP32S2
- tested successfully on FeatherS2

Airlift version works with SPI ESP32 module
- tested successfully on nrf52840 Feather + Airflit Featherwing

Original repository:
https://github.com/danni/uwebsockets
