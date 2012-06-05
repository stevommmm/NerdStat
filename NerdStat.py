#!/usr/bin/python
import curses 
import socket
import thread
from time import sleep

def get_info(host, port=25565):
	"""Server ping packet, ripped from Barneygale's brain"""
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(5.0)
	s.connect((host, port))
	s.send('\xfe')
	d = s.recv(256)
	s.close()
	assert d[0] == '\xff'
	d = d[3:].decode('utf-16be').split(u'\xa7')
	return {'motd':		str(d[0]),'players':	 str(d[1]),'max_players': str(d[2])}

def fancy_get_info(screenob,serv,line=0):
	"""Making our server info pretty"""
	try:
		stat = get_info(serv)
	except:
		stat = {'motd': serv, 'players': "?",'max_players': "?"}
	screenob.addstr(line,0,stat['motd'].ljust(25) + stat['players'].ljust(8) + stat['max_players'] + "\n")
	screenob.refresh()

def sock_test(server):
	"""Socket lookups, generally webservers"""
	cpos = server.find(':')
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((server[:cpos], int(server[cpos+1:])))
		sock.close
		return {'server':server[:cpos],'status':"up",'port':server[cpos+1:]}
	except:
		return {'server':server[:cpos],'status':"down",'port':server[cpos+1:]}

def fancy_sock_test(screenob,server,line=0):
	"""A helper method for sock_test, takes a curses screen object, the server name and output line as params"""
	stat = sock_test(server)
	screenob.addstr(line,0,stat['server'].ljust(25) + stat['status'].ljust(8) + stat['port'] + "\n")

def service_stats(screenob):
	"""	Our hardcoded service monitor
		Needs to be more configurable, ini file?"""
	screenob.clear() 
	screenob.addstr(9,0,"Updating...\n")
	screenob.refresh()
	# Get our headers in
	screenob.addstr(0,0,"Server".ljust(25) + "Players".ljust(8) + "Max \n",curses.A_UNDERLINE)
	screenob.addstr(5,0,"Services".ljust(25)+ "Status".ljust(8) + "Port\n",curses.A_UNDERLINE)
	screenob.refresh()
	# Check the servers themselves
	fancy_get_info(screenob,'c.nerd.nu',1)
	fancy_get_info(screenob,'s.nerd.nu',2)
	fancy_get_info(screenob,'p.nerd.nu',3)
	fancy_get_info(screenob,'x.nerd.nu',4)
	# Check some web services
	fancy_sock_test(screenob,'nerd.nu:80',6)
	fancy_sock_test(screenob,'mcbouncer.com:80',7)
	screenob.refresh()
	screenob.addstr(9,0,"Updated.\n")
	screenob.refresh()

def timed_update(screenob):
	"""A infinite loop with a sleeper, used to kick off the service stats update every 120s"""
	while 1:
		sleep(120)
		service_stats(screenob)

def main():
	"""A main method, because I can."""
	screen = curses.initscr() 
	curses.noecho() 
	curses.curs_set(0) 
	screen.keypad(1)
	screen.addstr("Welcome to the nerd.nu status tool.\n\n")
	screen.addstr("Auto updating every 2 minutes!\n")
	screen.addstr("Press R to force a status check.\n")
	screen.addstr("Press Q to quit.\n")
	thread.start_new_thread( timed_update , (screen,) ) #kick off an auto refresh
	while True: 
		event = screen.getch() 
		if event == ord("q"): break
		elif event == curses.KEY_DOWN:
			pass #removed kickoff
		elif event == ord("r"):
			service_stats(screen)
	curses.endwin()

if __name__ == "__main__":
	main()

