# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`websockets`
================================================================================

A library to connect to a websockets server.
Based on https://github.com/danni/uwebsockets

* Author(s): Neradoc

Implementation Notes
--------------------
**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/Neradoc/CircuitPython_websockets.git"

from .socket import UniversalSocket
from .client import connect


class Session:
    """
    Session class, used to configure the websocket client.
    Similar construction as the adafruit_requests version.
    """

    def __init__(self, socket_module, *, ssl=None, iface=None):
        self._usocket = UniversalSocket(
            socket_module,
            ssl=ssl,
            iface=iface,
        )

    def client(self, url, extra_headers=None):
        """
        Connect as a client to the given URL, and return the WebSocket object.
        Extra headers sent on connection can be added with the extra_headers dict.
        """
        return connect(url, self._usocket, extra_headers)
