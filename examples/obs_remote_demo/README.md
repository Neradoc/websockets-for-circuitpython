# OBS Websockets demo

This is a demo for a client for the OBS websockets plugin. It supports using either the native wifi module or an airlift breakout or feather wing. The default values set in the obs_pins.py file are set for the a Unexpected Maker Feather S2.

Requires `adafruit_hashlib` in addition to uwebsockets requirements.
To use, place all the files at the root of the Circuitpython drive, along with the `uwebsockets` directory, the `connect_circuitpython.py` file, and the filled in `secrets.py`.

To test it on your board you can change the `obs_pins.py` file:

-	Change the pins for the buttons.
-	Initialize the pixels (NeoPixel or DotStar, size of the strip).

The colors are setup the following way:

-	Define the colors in `obs_colors.py`.
-	Color patterns are used to represent a state.
-	Multiple states can be active at the same time (like recording and streaming).
-	The pixel(s) displays each state in turn with 1 second for each.
-	A color pattern does not need to change every pixel:
	-	If it contains `None`, the matching pixel is unchanged.
	-	This allows for assigning a different pixel for each state and not have it blink.
-	When we exit a state, we reset the pattern

The `obs_pins.py` and `obs_colors.py` files contain comments showing ways to set it up using an 8-pixels RGBW neopixel stick.


SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
SPDX-License-Identifier: MIT
