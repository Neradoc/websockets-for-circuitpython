# SPDX-FileCopyrightText: Copyright (c) 2019 Danielle Madeley
# SPDX-FileCopyrightText: Copyright (c) 2021 Neradoc
#
# SPDX-License-Identifier: MIT
"""
`websockets.protocol`
================================================================================

* Author(s): Danielle Madeley, Neradoc
"""
# pylint: disable=invalid-name

import random
import re
import struct
from collections import namedtuple
from micropython import const
import adafruit_logging as logging

LOGGER = logging.getLogger(__name__)

# Opcodes
_OP_CONT = const(0x0)
_OP_TEXT = const(0x1)
_OP_BYTES = const(0x2)
_OP_CLOSE = const(0x8)
_OP_PING = const(0x9)
_OP_PONG = const(0xA)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)

URL_RE = re.compile(r"(wss|ws)://([A-Za-z0-9-\.]+)(?:\:([0-9]+))?(/.+)?")
URI = namedtuple("URI", ("protocol", "hostname", "port", "path"))


class NoDataException(Exception):
    """No data received unexpectedly"""


class ConnectionClosed(Exception):
    """Connection closed"""


def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        protocol = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path = match.group(4)

        if protocol == "wss":
            if port is None:
                port = 443
        elif protocol == "ws":
            if port is None:
                port = 80
        else:
            raise ValueError("Scheme {} is invalid".format(protocol))

        return URI(protocol, host, int(port), path)

    raise ValueError("URL invalid. Format: ws[s]://server:port/[path]")


class Websocket:
    """
    Basis of the Websocket protocol.
    """

    is_client = False

    def __init__(self, sock):
        self.sock = sock
        self.open = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def settimeout(self, timeout):
        """Set the timeout of the underlying socket"""
        self.sock.settimeout(timeout)

    def read_frame(self):  # max_size=None
        """
        Read a frame from the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """

        # Frame header
        two_bytes = self.sock.read(2)

        if not two_bytes:
            raise NoDataException

        byte1, byte2 = struct.unpack("!BB", two_bytes)

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0F

        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7F

        if length == 126:  # Magic number, length header is 2 bytes
            (length,) = struct.unpack("!H", self.sock.read(2))
        elif length == 127:  # Magic number, length header is 8 bytes
            (length,) = struct.unpack("!Q", self.sock.read(8))

        if mask:  # Mask is 4 bytes
            mask_bits = self.sock.read(4)

        try:
            data = self.sock.read(length)
        except MemoryError:
            # We can't receive this many bytes, close the socket
            if __debug__:
                LOGGER.debug("Frame of length %s too big. Closing", length)
            self.close(code=CLOSE_TOO_BIG)
            return True, _OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b""):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self.sock.send(struct.pack("!BB", byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self.sock.send(struct.pack("!BBH", byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self.sock.send(struct.pack("!BBQ", byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack("!I", random.getrandbits(32))
            self.sock.send(mask_bits)

            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        self.sock.send(data)

    def recv(self):
        """
        Receive data from the websocket.

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        """
        assert self.open

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                return ""
            except ValueError:
                LOGGER.debug("Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()  # pylint: disable=raise-missing-from

            if not fin:
                raise NotImplementedError()

            if opcode == _OP_TEXT:
                return data.decode("utf-8")
            if opcode == _OP_BYTES:
                return data
            if opcode == _OP_CLOSE:
                self._close()
                raise ConnectionClosed(opcode)
            if opcode == _OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            if opcode == _OP_PING:
                # We need to send a pong frame
                if __debug__:
                    LOGGER.debug("Sending PONG")
                self.write_frame(_OP_PONG, data)
                # And then wait to receive
                continue
            if opcode == _OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            # nothing
            raise ValueError(opcode)

    def send(self, buf):
        """Send data to the websocket."""

        assert self.open

        if isinstance(buf, str):
            opcode = _OP_TEXT
            buf = buf.encode("utf-8")
        elif isinstance(buf, bytes):
            opcode = _OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=""):
        """Close the websocket."""
        if not self.open:
            return

        buf = struct.pack("!H", code) + reason.encode("utf-8")

        self.write_frame(_OP_CLOSE, buf)
        self._close()

    def _close(self):
        if __debug__:
            LOGGER.debug("Connection closed")
        self.open = False
        self.sock.close()
