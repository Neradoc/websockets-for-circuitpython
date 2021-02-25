"""
Websockets client for micropython

Based on
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import random
import adafruit_logging as logging
import adafruit_binascii as binascii

from .protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)

class WebsocketClient(Websocket):
    is_client = True

def connect(uri, socket_module):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__: LOGGER.debug("open connection %s:%s",
                                uri.hostname, uri.port)

    addr_info = socket_module.getaddrinfo(
        uri.hostname, uri.port, 0, socket_module.SOCK_STREAM
    )[0]
    sock = socket_module.socket(
        addr_info[0], addr_info[1]
    )
    connect_host = addr_info[-1][0]

    if uri.protocol == 'wss':
        connect_host = uri.hostname
        connect_mode = socket_module.TLS_MODE
    else:
        connect_mode = socket_module.TCP_MODE

    if __debug__: LOGGER.debug(str((connect_host,uri.port)))
    #r = sock.connect((connect_host,uri.port), connect_mode)
    r = sock.connect((connect_host,uri.port),connect_mode)

    def send_header(header, *args):
        if __debug__: LOGGER.debug(str(header), *args)
        sock.send((header % args) + b'\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]

    send_header(b'GET %s HTTP/1.1', uri.path or '/')
    send_header(b'Host: %s:%s', uri.hostname, uri.port)
    send_header(b'Connection: Upgrade')
    send_header(b'Upgrade: websocket')
    send_header(b'Sec-WebSocket-Key: %s', key.decode())
    send_header(b'Sec-WebSocket-Version: 13')
    send_header(b'Origin: http://%s:%s', uri.hostname, uri.port)
    send_header(b'')

    header = sock.readline()
    assert header.startswith(b'HTTP/1.1 101 '), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: LOGGER.debug(str(header))
        header = sock.readline()

    return WebsocketClient(sock)
