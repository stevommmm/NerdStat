#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
import json
import collections
import time
import sys
import threading

class Color(object):
	reset = chr(27) + "[0m"
	header = chr(27) + "[33m"
	value = chr(27) + "[36m"
	clear = chr(27) + "[2J" + chr(27) + "[H"

class Spark(object):
	def __init__(self, maxlen = 60):
		self.data = collections.deque([], maxlen)

	def append(self, val):
		self.data.append(val)

	def last(self):
		try:
			return self.data[-1]
		except:
			return "?"

	def _sparkpoint(self, value, min_range, step, ticks):
		if not type(value) is int:
			return "?"
		return ticks[int(round((value - min_range) / step))]

	def render(self):
		if len(self.data) == 0:
			return ''
		min_range = 0
		# min_range = min(self.data)
		ticks = u'▁▂▃▅▆▇'
		step_range = max(filter(lambda x:type(x) == int, self.data)) - min_range
		step = ((step_range) / float(len(ticks) - 1)) or 1
		return u''.join(self._sparkpoint(i, min_range, step, ticks) for i in self.data)


class MCServer(object):
	def __init__(self, server, port = 25565):
		self.server = server
		self.port = port
		self.history = Spark()
		self.description = "???"

	def unpack_varint(self, s):
		d = 0
		for i in range(5):
			b = ord(s.recv(1))
			d |= (b & 0x7F) << 7*i
			if not b & 0x80:
				break
		return d
	 
	def pack_varint(self, d):
		o = ""
		while True:
			b = d & 0x7F
			d >>= 7
			o += struct.pack("B", b | (0x80 if d > 0 else 0))
			if d == 0:
				break
		return o
	 
	def pack_data(self, d):
		return self.pack_varint(len(d)) + d
	 
	def pack_port(self, i):
		return struct.pack('>H', i)
	 
	def get_info(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.server, self.port))
		# Send handshake + status request
		s.send(self.pack_data("\x00\x00" + self.pack_data(self.server.encode('utf8')) + self.pack_port(self.port) + "\x01"))
		s.send(self.pack_data("\x00"))
		# Read response
		self.unpack_varint(s)     # Packet length
		self.unpack_varint(s)     # Packet ID
		l = self.unpack_varint(s) # String length
		d = ""
		while len(d) < l:
			d += s.recv(1024)
		# Close our socket
		s.close()
		# Load json and return
		return json.loads(d.decode('utf8'))

	def update(self):
		try:
			info = self.get_info()
			self.history.append(info['players']['online'])
			self.description = info['description']
		except:
			self.history.append("?")

	def render(self):
		return (Color.header, self.description[:30].ljust(31), Color.reset, Color.value, str(self.history.last()).ljust(4), Color.reset, self.history.render())

def timedUpdater():
	while True:
		for s in servers:
			s.update()
		time.sleep(60)

def printLoop():
	while True:
		sys.stdout.write(Color.clear + Color.reset)
		sys.stdout.write("\n".join(map( lambda s:''.join(s.render()), servers)))
		sys.stdout.flush()
		time.sleep(20)

if __name__ == '__main__':
	servers = [
		MCServer('p.nerd.nu'),
		MCServer('s.nerd.nu'),
		MCServer('c.nerd.nu'),
	]

	t = threading.Thread(target=timedUpdater)
	t.setDaemon(True)
	t.start()
	time.sleep(2)
	try:
		printLoop()
	except KeyboardInterrupt:
		print 'Got ctrl + C'
	
