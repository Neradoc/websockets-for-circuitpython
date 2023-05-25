# SPDX-FileCopyrightText: Copyright (c) 2019 Danielle Madeley
# SPDX-FileCopyrightText: Copyright (c) 2021 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`websockets.client`
================================================================================

* Author(s): Danielle Madeley, Neradoc
"""

import binascii
import random
import adafruit_logging as logging

from .protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)


class WebsocketClient(Websocket):
    """Web socket client wrapper class"""

    is_client = True


def connect(uri, socket_module, extra_headers=None):
    """
    Connect a websocket.
    The uri is a string with ws or wss url scheme.
    The socket module is a module that matches the C python socket module API.
    Extra headers sent on connection can be added with the extra_headers dict.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__:
        LOGGER.debug("open connection %s:%s", uri.hostname, uri.port)

    addr_info = socket_module.getaddrinfo(
        uri.hostname, uri.port, 0, socket_module.SOCK_STREAM
    )[0]
    sock = socket_module.socket(addr_info[0], addr_info[1])
    connect_host = addr_info[-1][0]

    if uri.protocol == "wss":
        connect_host = uri.hostname
        connect_mode = socket_module.TLS_MODE
        https = "s"
    else:
        connect_mode = socket_module.TCP_MODE
        https = ""

    if __debug__:
        LOGGER.debug(str((connect_host, uri.port)))

    sock.connect((connect_host, uri.port), connect_mode)

    def send_header(header, *args):
        output = header.format(*args)
        if __debug__:
            LOGGER.debug(output)
        return sock.send(output.encode() + b"\r\n")

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)))[:-1]
    send_header("GET {} HTTP/1.1", uri.path or "/")
    send_header("Host: {}:{}", uri.hostname, uri.port)
    send_header("Connection: Upgrade")
    send_header("Upgrade: websocket")
    send_header("Sec-WebSocket-Key: {}", key.decode())
    send_header("Sec-WebSocket-Version: 13")
    send_header("Origin: http{}://{}:{}", https, uri.hostname, uri.port)
    # additional headers
    if extra_headers:
        for extra_header_key in extra_headers:
            send_header("{}: {}", extra_header_key, extra_headers[extra_header_key])
    send_header("")

    header = sock.readline()
    if not header.startswith(b"HTTP/1.1 101 "):
        raise ConnectionError(header)

    # We don't (currently) need these headers should we check the returned key?
    while header:
        if __debug__:
            LOGGER.debug(str(header))
        header = sock.readline()

    return WebsocketClient(sock)
