'''
Macro handler, runs from file
'''

from threading import Thread
import pyautogui as pygui
from pyautogui import FailSafeException
import os, csv, time

class MacroError(Exception):
	pass

class MacroFailSafeException(MacroError):
	pass

def config(pause=None, failsafe=None):
	if pause:
		pygui.PAUSE = float(pause)
	elif failsafe:
		if failsafe.lower() == 'true':
			pygui.FAILSAFE = True
		elif failsafe.lower() == 'false':
			pygui.FAILSAFE = False
		else:
			raise TypeError(f'Expected type boolean, got "{failsafe}"')

def keyword(*args):
	'''Dummy function, in case keywords are seen as commands'''
	pass

COMMANDS = {
	'config' : config,
  'moveTo' : pygui.moveTo,
  'move' : pygui.move,
  'mouseDown' : pygui.mouseDown,
  'mouseUp' : pygui.mouseUp,
  'click' : pygui.click,
  'dragTo' : pygui.dragTo,
  'drag' : pygui.drag,
  'scroll' : pygui.scroll,
  'write' : pygui.write,
  'keyDown' : pygui.keyDown,
  'keyUp' : pygui.keyUp,
  'press' : pygui.press,
	'hotkey' : pygui.hotkey,
	'wait' : pygui.sleep,
	'repeat' : keyword,
	'exit' : keyword
}


class Controller(Thread):
	def __init__(self, userCommands=dict()):
		super().__init__()
		self.COMMANDS = dict(**COMMANDS, **userCommands)
		self.status = False
		self.daemon = True
		self._running = True
		self.filepath = None
		self.mode = 'once'

	def _load(self, filepath: str):
		'''File loader, reads file line by line'''
		with open(filepath, 'r') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				yield row

	def _runcmd(self, cmdlist: list):
		'''Dispatch Method, runs pyautogui functions'''
		cmdname = cmdlist.pop(0)
		for i in range(len(cmdlist)):
			if cmdlist[i] == ('NoneType', ''):
				cmdlist[i] = None
		if cmdname == 'repeat':
			self._repeat(*cmdlist)
		else:
			command = self.COMMANDS.get(cmdname)
			kwargs = {}
			for param in cmdlist:
				kw, arg = param.split('=', 1)
				kwargs[kw.strip()] = arg.strip()
			try:
				command(**kwargs)
			except FailSafeException as exc:
				raise MacroFailSafeException from exc

	def _compiler(self, filepath: str):
		'''Compiles the code into something the program can read'''
		indentations = 0
		cmdlist = list()
		repeatqueue = list()
		for cmdline in self._load(filepath):
			if indentations:
				# if in repeat function, get all commands until we reach an 'exit' keyword
				for i in range(len(cmdline[:indentations])):
					# detect if a repeat has been broken
					if cmdline[indentations-1-i] != '':
						cmdlist.append(repeatqueue)
						indentations = indentations-1-i
						cmdlist.append(cmdline[indentations:])
						break
				else:
					repeatqueue[2].append(cmdline[indentations:])
			else:
				if cmdline[0] == 'repeat':
					repeatqueue = [cmdline[0], cmdline[1], []]
					indentations += 1
				else:
					cmdlist.append(cmdline[indentations:])
		return cmdlist
			

	def _repeat(self, amt, cmdlist: list):
		'''Code for repeater function'''
		for _ in range(int(amt)):
			for i in cmdlist:
				try:
					self._runcmd(i)
				except MacroFailSafeException as exc:
					raise MacroFailSafeException from exc

	def _runFile(self, filepath: str):
		'''Base run function, not meant to be used when calling this class'''
		cmdlist = self._compiler(filepath)
		for i in cmdlist:
			try:
				if self.status:
					self._runcmd(i)
				else:
					break
			except MacroFailSafeException as exc:
				self.status = False
				raise MacroFailSafeException(
			"PyAutoGUI fail-safe triggered from mouse moving to a corner of the screen. To disable this fail-safe, do '|config|FAILSAFE|false|'. DISABLING FAIL-SAFE IS NOT RECOMMENDED."
			) from exc
			except Exception as e:
				self.status = False
				raise e from e

	def start_macro(self, filepath: str, mode: str='once'):
		'''Starts the macro'''
		if not self.status:
			self.status = True
			self.filepath = filepath
			self.mode = mode

	def stop_macro(self):
		'''Stops the current instance of this macro runner'''
		if self.status:
			self.status = False

	def run(self):
		'''Main function, runs the file specified'''
		while self._running:
			if self.status:
				if self.mode == 'forever':
					while self.status:
						self._runFile(self.filepath)
				elif self.mode == 'once':
					self._runFile(self.filepath)
				else:
					for _ in range(int(self.mode)):
						if self.status:
							self._runFile(self.filepath)
						else:
							break
				self.stop_macro()
			time.sleep(0.01)

	def exit(self):
		self.stop_macro()
		self._running = False