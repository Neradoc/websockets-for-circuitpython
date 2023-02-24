# Cpython websocket client/server demo

To use, first run the server demo on your computer:

-	use pip to install `asyncio` and `aioconsole`
-	run `server.py` with python 3

And place the following files at the root of the Circuitpython drive.

-	`client.py`
-	`connect_circuitpython.py`
-	`status_led.py`
-	`uwebsockets` directory
-	`secrets.py` (filled in)

Once the board connects to the server, the server script should prompt you for a color, which will then be displayed on the status LED of the board.

Accepted formats include:

-	hexadecimal html color `0xFFFFFF`
-	decimal version of that `16777215`
-	list of decimal RGB values `(255,255,255)` or `[255,255,255]`
-	any of: `aqua` `black` `blue` `green` `magenta` `orange` `pink` `purple` `red` `turquoise` `white` `yellow`

From the board side, you can press buttons, if there are buttons configured, look in the `client.py` script. The buttons pressed will be printed out on the server console.


SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
SPDX-License-Identifier: MIT
