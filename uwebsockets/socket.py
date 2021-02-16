"""
Universal socket
"""

BUFFER_SIZE = const(32)

class UniversalSocket:
	TCP_MODE = 1
	TLS_MODE = 2
	UDP_MODE = 4

	def __init__(self,socket,*,ssl=None,iface=None):
		self.socketModule = socket
		self._socket = None
		self.buffer = None
		self.ssl_context = ssl
		self.iface = iface
		#if not hasattr(self._socket,"read"):
		#	if not hasattr(self._socket,"recv_into"):
		#		raise "Socket type not supported"
		self.buffer = bytearray(BUFFER_SIZE)

	def readline(self):
		if hasattr(self._socket,"readline"):
			return self._socket.readline()
		else:
			dataString = b""
			while True:
				num = self._socket.recv_into(self.buffer,1)
				dataString += self.buffer[:num]
				if num == 0:
					return dataString
				if dataString[-2:] == b"\r\n":
					return dataString[:-2]

	def read(self,length):
		if hasattr(self._socket,"read"):
			return self._socket.read(length)
		else:
			total = 0
			dataString = b""
			while total < length:
				reste = length - total
				num = self._socket.recv_into(self.buffer,min(BUFFER_SIZE,reste))
				#
				if num == 0:
					# timeout
					raise OSError(110)
				#
				dataString += self.buffer[:num]
				total = total + num
			return dataString

	# settimeout, send, close
	def __getattr__(self,attr):
		if self._socket and hasattr(self._socket,attr):
			return getattr(self._socket,attr)
		elif hasattr(self.socketModule,attr):
			return getattr(self.socketModule,attr)
		elif hasattr(self.iface,attr):
			return getattr(self.iface,attr)
		else:
			raise AttributeError(f"'UniversalSocket' object has no attribute '{attr}'")

	def connect(self,hostname,port = None, mode = 1):
		if mode == self.TLS_MODE:
			if self.ssl_context:
				self._socket = self.ssl_context.wrap_socket(self._socket, server_hostname = hostname)
			if port == None:
				port = 443
		else:
			if port == None:
				port = 80
		#
		if self.iface is not None:
			if mode == self.TLS_MODE:
				connect_mode = self.iface.TLS_MODE
			if mode == self.TCP_MODE:
				connect_mode = self.iface.TCP_MODE
			return self._socket.connect((hostname,port),connect_mode)
		#else:
		return self._socket.connect((hostname,port))

	def getaddrinfo(self,*args):
		return self.socketModule.getaddrinfo(*args)
	
	def socket(self,*args):
		self._socket = self.socketModule.socket(*args)
		return self
