#!/usr/bin/python
import curses
import socket
import thread
import operator

from time import sleep

screen = None

padding = {'protocol_version': [4, "p_v"], 'server_version': [6, "s_v"], 'motd': [50, "motd"], 'players': [5, "plrs"], 'max_players': [5, "max"]}

def get_info(host='localhost', port=25565):
    #Set up our socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((host, port))
    #Send 0xFE: Server list ping
    s.send('\xfe\x01')
    
    #Read some data
    d = s.recv(1024)
    s.close()
    
    #Check we've got a 0xFF Disconnect
    assert d[0] == '\xff'
    
    #Remove the packet ident (0xFF) and the short containing the length of the string
    #Decode UCS-2 string
    d = d[3:].decode('utf-16be')
    
    #Check the first 3 characters of the string are what we expect
    assert d[:3] == u'\xa7\x31\x00'
    
    #Split
    d = d[3:].split('\x00')
    
    #Return a dict of values
    return {'protocol_version': int(d[0]),
            'server_version':       d[1],
            'motd':                 d[2],
            'players':          int(d[3]),
            'max_players':      int(d[4])}

def test(host):
	try:
		screen.addstr(prst(get_info(host)))
	except:
		pass
	finally:
		screen.refresh()

def prst(valdict):
	retstr = []
	for key, value in sorted(valdict.iteritems(), key=operator.itemgetter(0)):
		retstr.append(str(value).strip().ljust(padding[key][0]))
	return "".join(retstr) + "\n"

def service_stats():
	""" Our hardcoded service monitor
		Needs to be more configurable, ini file?"""
	global curr_line
	curr_line = 1
	screen.clear()
	# Get our headers in
	screen.addstr("".join([y[1].ljust(y[0]) for x,y in sorted(padding.iteritems(), key=operator.itemgetter(0))])  + "\n",curses.color_pair(1))
	screen.refresh()
	# Check the servers themselves
	test('c.nerd.nu')
	test('s.nerd.nu')
	test('p.nerd.nu')
	test('x.nerd.nu')
	test('event.nerd.nu')
	test('hcsmp.com')
	screen.refresh()

def timed_update():
	"""A infinite loop with a sleeper, used to kick off the service stats update every 120s"""
	while 1:
		sleep(120)
		service_stats()

if __name__ == "__main__":
	screen = curses.initscr()
	curses.noecho()
	curses.curs_set(0)
	screen.keypad(1)
	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	screen.scrollok(True)
	screen.addstr("Welcome to the nerd.nu status tool.\n\n")
	screen.addstr("Auto updating every 2 minutes!\n")
	screen.addstr("Press R to force a status check.\n")
	screen.addstr("Press Q to quit.\n")
	thread.start_new_thread( timed_update , () ) #kick off an auto refresh
	while True:
		event = screen.getch()
		if event == ord("q"): break
		elif event == ord("r"):
			service_stats()
	curses.endwin()
