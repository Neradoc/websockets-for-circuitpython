# SPDX-FileCopyrightText: Copyright (c) 2021 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`websockets`
================================================================================

Universal socket for abstracting ESP32SPI/native wifi

* Author(s): Neradoc
"""

import errno
from micropython import const

TCP_MODE = 1
TLS_MODE = 2
UDP_MODE = 4
_BUFFER_SIZE = const(32)


class UniversalSocket:
    """
    Socket class for compatibility with native wifi and ESP32SPI wifi.
    """

    TCP_MODE = TCP_MODE
    TLS_MODE = TLS_MODE
    UDP_MODE = UDP_MODE

    def __init__(self, socket, *, ssl=None, iface=None):
        self.socket_module = socket
        self._socket = None
        self.buffer = None
        self.ssl_context = ssl
        self.iface = iface
        self.buffer = bytearray(_BUFFER_SIZE)

    def readline(self):
        """
        Implement readline() for native wifi using recv_into
        """
        if hasattr(self._socket, "readline"):
            return self._socket.readline()

        data_string = b""
        while True:
            num = self._socket.recv_into(self.buffer, 1)
            data_string += self.buffer[:num]
            if num == 0:
                return data_string
            if data_string[-2:] == b"\r\n":
                return data_string[:-2]

    def read(self, length):
        """
        Implement read() for native wifi using recv_into
        """
        if hasattr(self._socket, "read"):
            return self._socket.read(length)

        total = 0
        data_string = b""
        while total < length:
            reste = length - total
            num = self._socket.recv_into(self.buffer, min(_BUFFER_SIZE, reste))
            #
            if num == 0:
                # timeout
                raise OSError(errno.ETIMEDOUT)
            #
            data_string += self.buffer[:num]
            total = total + num
        return data_string

    # settimeout, send, close
    def __getattr__(self, attr):
        if self._socket and hasattr(self._socket, attr):
            # we are a socket
            return getattr(self._socket, attr)
        if hasattr(self.socket_module, attr):
            # we are also the socket module
            return getattr(self.socket_module, attr)
        if hasattr(self.iface, attr):
            # we could be the interface ?
            # TODO: remove that ?
            return getattr(self.iface, attr)
        raise AttributeError(f"'UniversalSocket' object has no attribute '{attr}'")

    def connect(self, host, mode=TCP_MODE):
        """
        Connect to the host = (hostname,port) with the mode (TCP/TLS supported)
        Wrapping with the ssl_context happens here, not done by the outside code
        """
        hostname, port = host
        if mode == self.TLS_MODE:
            if self.ssl_context:
                self._socket = self.ssl_context.wrap_socket(
                    self._socket, server_hostname=hostname
                )
            if port is None:
                port = 443
        else:
            if port is None:
                port = 80
        #
        if self.iface is not None:
            if mode == self.TLS_MODE:
                connect_mode = self.iface.TLS_MODE
            if mode == self.TCP_MODE:
                connect_mode = self.iface.TCP_MODE
            return self._socket.connect((hostname, port), connect_mode)
        # else:
        return self._socket.connect((hostname, port))

    # TODO: remove (stick with getattr)
    def getaddrinfo(self, *args):
        """Get address info from the underlying socket module"""
        return self.socket_module.getaddrinfo(*args)

    def socket(self, *args):
        """
        We are the socket, as well as the socket module
        """
        self._socket = self.socket_module.socket(*args)
        return self
