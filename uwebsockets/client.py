"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

import time
import adafruit_logging as logging
import adafruit_binascii as binascii
import random
# circuitpython special
import socketpool,wifi,ssl

from .protocol import Websocket, urlparse

LOGGER = logging.getLogger(__name__)


class WebsocketClient(Websocket):
    is_client = True

def readline(sock):
    # \r\n
    buffer =  bytearray(4)
    dataString = ""
    while True:
        num = sock.recv_into(buffer,1)
        dataString += str(buffer, 'utf8')[:num]
        if num == 0:
            return dataString
        if dataString[-2:] == "\r\n":
            return dataString

def connect(uri):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__: LOGGER.debug("open connection %s:%s",
                                uri.hostname, uri.port)

    pool = socketpool.SocketPool(wifi.radio)
    addr_info = pool.getaddrinfo(
        uri.hostname, uri.port, 0, pool.SOCK_STREAM
    )[0]
    sock = pool.socket(
        addr_info[0], addr_info[1], addr_info[2]
    )
    connect_host = addr_info[-1][0]
    if uri.protocol == 'wss':
        ssl_context = ssl.create_default_context()
        sock = ssl_context.wrap_socket(sock,server_hostname = uri.hostname)
        connect_host = uri.hostname # that's what I was missing
    r = sock.connect((connect_host,uri.port))

    def send_header(header, *args):
        if __debug__: LOGGER.debug(str(header), *args)
        sock.send((header % args) + b'\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]

    send_header(b'GET %s HTTP/1.1', uri.path or '/')
    send_header(b'Host: %s:%s', uri.hostname, uri.port)
    send_header(b'Origin: http://localhost')
    send_header(b'Upgrade: websocket')
    send_header(b'Connection: Upgrade')
    send_header(b'Sec-WebSocket-Key: '+key)
    send_header(b'Sec-WebSocket-Version: 13')
    send_header(b'')

    header = readline(sock)[:-2]
    assert header.startswith(b'HTTP/1.1 101 '), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: LOGGER.debug(str(header))
        header = readline(sock)[:-2]

    return WebsocketClient(sock)
