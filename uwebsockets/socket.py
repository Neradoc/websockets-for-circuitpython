"""
Universal socket
"""

TCP_MODE = 1
TLS_MODE = 2
UDP_MODE = 4
_BUFFER_SIZE = const(32)


class UniversalSocket:
	TCP_MODE = TCP_MODE
	TLS_MODE = TLS_MODE
	UDP_MODE = UDP_MODE

	def __init__(self, socket, *, ssl=None, iface=None):
		self.socket_module = socket
		self._socket = None
		self.buffer = None
		self.ssl_context = ssl
		self.iface = iface
		# if not hasattr(self._socket,"read"):
		#     if not hasattr(self._socket,"recv_into"):
		#         raise "Socket type not supported"
		self.buffer = bytearray(_BUFFER_SIZE)

	def readline(self):
		if hasattr(self._socket, "readline"):
			return self._socket.readline()
		else:
			data_string = b""
			while True:
				num = self._socket.recv_into(self.buffer, 1)
				data_string += str(self.buffer, 'utf8')[:num]
				if num == 0:
					return data_string
				if data_string[-2:] == b"\r\n":
					return data_string[:-2]

	def read(self, length):
		if hasattr(self._socket, "read"):
			return self._socket.read(length)
		else:
			total = 0
			data_string = b""
			while total < length:
				reste = length - total
				num = self._socket.recv_into(self.buffer, min(_BUFFER_SIZE, reste))
				#
				if num == 0:
					# timeout
					raise OSError(110)
				#
				data_string += self.buffer[:num]
				total = total + num
			return data_string

	# settimeout, send, close
	def __getattr__(self, attr):
		if self._socket and hasattr(self._socket, attr):
			return getattr(self._socket, attr)
		elif hasattr(self.socket_module, attr):
			return getattr(self.socket_module, attr)
		elif hasattr(self.iface, attr):
			return getattr(self.iface, attr)
		else:
			raise AttributeError(f"'UniversalSocket' object has no attribute '{attr}'")

	def connect(self, host, mode=1):
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

	def getaddrinfo(self, *args):
		return self.socket_module.getaddrinfo(*args)

	def socket(self, *args):
		self._socket = self.socket_module.socket(*args)
		return self
