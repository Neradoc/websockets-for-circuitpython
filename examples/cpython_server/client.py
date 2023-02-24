"""
Client/Server demo for websockets

The client receives colors from the server and changes the status LED
according to it. The client listens to buttons on the board and sends
messages to the server just so they know.

Requirements from the examples directory:
- connect_circuitpython.py
- status_led.py
"""
## set debug to False for future imports (removes logging)
import micropython

micropython.opt_level(1)

import json
import os
import sys
import time
import errno

"""
Setup button inputs, reasonnable defaults for some boards.
"""
import board
from digitalio import DigitalInOut, Pull

buttons = []
bname = os.uname().machine.lower()
if bname.find("magtag"):
    buttons = [
        (board.D11, Pull.UP, False, "right"),
        (board.D12, Pull.UP, False, "bottom"),
        (board.D14, Pull.UP, False, "top"),
        (board.D15, Pull.UP, False, "left"),
    ]
elif bname.find("feathers2") >= 0:
    buttons = [
        (board.D0, Pull.UP, "boot"),
    ]

for i in range(len(buttons)):
    btn = DigitalInOut(buttons[i][0])
    btn.switch_to_input(buttons[i][1])
    buttons[i] = (
        btn,
        buttons[i][2],
        buttons[i][3],
    )

"""
Setup internet and websockets connection
"""
from secrets import secrets
from status_led import status_led
from connect_circuitpython import connect_wifi
from uwebsockets import Session

socket, ssl_context, iface = connect_wifi()
wsession = Session(socket, ssl=ssl_context, iface=iface)

url = "ws://{}:{}/index".format(secrets["test_server"], secrets.get("test_port", 5000))

"""
Loop-de-loop
"""
print(f"Connecting to {url}")
with wsession.client(url) as ws:
    was_pressed = []
    print(">", "START")
    ws.send(json.dumps({"start": "START"}))
    ws.settimeout(0.1)
    while True:
        # recv from the server
        try:
            result = ws.recv()
        except OSError as err:
            if err.args[0] == errno.ETIMEDOUT:
                result = None
            else:
                raise

        # react to the server
        if result != None:
            try:
                data = json.loads(result)
            except:
                data = {}
            if "color" in data:
                try:
                    color = data["color"]
                    print(f"Color: {color}")
                    status_led.fill(color)
                    status_led.show()
                except:
                    print(f"ERREUR de couleur {data['color']}")
            if "response" in data:
                print("<", data["response"])

        # listen to the buttons
        list_buttons = []
        message_buttons = {}
        for button in buttons:
            if button[0].value == button[1]:
                list_buttons.append(button[2])
                if button[2] not in was_pressed:
                    message_buttons[button[2]] = "pressed"
            elif button[2] in was_pressed:
                message_buttons[button[2]] = "released"
        if len(message_buttons) > 0:
            button_message = json.dumps({"buttons": message_buttons})
            print(">", button_message)
            ws.send(button_message)
        was_pressed = list_buttons
