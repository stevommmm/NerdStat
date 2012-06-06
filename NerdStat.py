#!/usr/bin/python
import curses
import socket
import thread
import requests

from time import sleep

mc_username = None
mc_password = None
screen = None
curr_line = 0

pad = [25,8,5]

def get_info(host, port=25565):
	"""Server ping packet, ripped from Barneygale's brain"""
	global curr_line
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(5.0)
		s.connect((host, port))
		s.send('\xfe')
		d = s.recv(256)
		s.close()
		assert d[0] == '\xff'
		d = d[3:].decode('utf-16be').split(u'\xa7')
		screen.addstr(curr_line,0,str(d[0]).ljust(pad[0]) + str(d[1]).ljust(pad[1]) + str(d[2]).ljust(pad[2]))
	except:
		screen.addstr(curr_line,0,host.ljust(pad[0]) + "?".ljust(pad[1]) + "?".ljust(pad[2]))
	finally:
		curr_line  += 1
		screen.refresh()

def sock_test(server):
	"""Socket lookups, generally webservers"""
	global curr_line
	cpos = server.find(':')
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((server[:cpos], int(server[cpos+1:])))
		sock.close
		screen.addstr(curr_line,0,server[:cpos].ljust(pad[0]) + "up".ljust(pad[1]) + server[cpos+1:].ljust(pad[2]))
	except:
		screen.addstr(curr_line,0,server[:cpos].ljust(pad[0]) + "down".ljust(pad[1]) + server[cpos+1:].ljust(pad[2]))
	finally:
		curr_line  += 1
		screen.refresh()

def mcnetStatus():
	global curr_line
	loginStatus = 'down'
	loginCode = '-'
	sessionStatus = 'down'
	sessionCode = '-'

	try:
		login = requests.post('https://login.minecraft.net', timeout=4, data={ 'user': mc_username, 'password': mc_password, 'version': 9001 })
		if login.status_code == requests.codes.ok:
			loginStatus = 'up'
		loginCode = str(login.status_code)
	except requests.exceptions.Timeout:
		loginCode = 'Timeout'
	screen.addstr(curr_line, 0, 'Login'.ljust(pad[0]) + loginStatus.ljust(pad[1]) + loginCode + "\n")
	curr_line  += 1
	screen.refresh()
	try:
		session = requests.get('http://session.minecraft.net/game/joinserver.jsp', timeout=5, params={ 'user': 'fakeUsername', 'sessionId': 'invalid_sessionID', 'serverId': 'randomtext' })
		if session.status_code == requests.codes.ok:
			sessionStatus = 'up'
		sessionCode = str(session.status_code)
	except requests.exceptions.Timeout:
		sessionCode = 'timeout'
	screen.addstr(curr_line, 0, 'Session'.ljust(pad[0]) + sessionStatus.ljust(pad[1]) + sessionCode + "\n")
	curr_line  += 1
	screen.refresh()

def service_stats():
	""" Our hardcoded service monitor
		Needs to be more configurable, ini file?"""
	global curr_line
	curr_line = 1
	screen.clear()
	screen.addstr(13,0,"Updating...\n")
	screen.refresh()
	# Get our headers in
	screen.addstr(0,0,"Server".ljust(pad[0]) + "Players".ljust(pad[1]) + "Max".ljust(pad[2]) + "\n",curses.color_pair(1))
	screen.refresh()
	# Check the servers themselves
	get_info('c.nerd.nu')
	get_info('s.nerd.nu')
	get_info('p.nerd.nu')
	get_info('x.nerd.nu')
	# Check some web services
	screen.addstr(curr_line,0,"Services".ljust(pad[0])+ "Status".ljust(pad[1]) + "Port".ljust(pad[2]) + "\n",curses.color_pair(1))
	curr_line += 1
	sock_test('nerd.nu:80')
	sock_test('mcbouncer.com:80')
	screen.addstr(13 ,0 ,"\n")
	# Check minecraft.net login & session servers
	#screen.addstr(curr_line,0,"Minecraft.net".ljust(pad[0])+ "Status".ljust(pad[1]) +"Code".ljust(pad[2]) + "\n",curses.color_pair(1))
	#curr_line += 1
	#mcnetStatus()
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
