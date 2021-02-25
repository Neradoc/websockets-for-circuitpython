# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`websockets`
================================================================================

An implementation of WebSockets for Circuitpython


* Author(s): Neradoc

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/Neradoc/CircuitPython_WebSockets.git"

from .socket import UniversalSocket
from .client import connect

class Session:
    def __init__(self, socket_module, *, ssl=None, iface=None):
        self._usocket = UniversalSocket(
            socket_module,
            ssl=ssl,
            iface=iface,
        )

    def client(self, url):
        """
        Connect as a client to the given URL, and return the WebSocket object
        """
        return connect(url, self._usocket)
