from Macro import Controller
from tkinter import ttk
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
from ttkthemes import ThemedStyle
from pynput.keyboard import Listener, Key, KeyCode
import os

window = tk.Tk()
window.title('Macro Mk2')
window['bg']='white'
window.geometry('456x202')
window.columnconfigure([0, 1], weight=1)
window.rowconfigure([0, 1, 2], weight=1)
window.attributes('-topmost', True)

style = ThemedStyle(window)
style.theme_use('arc')
theme = 'arc'

hotkeyButton = Key.f5
filePath = None

def initListener():
  global listener
  def on_release(key):
    if key == hotkeyButton:
      configure()
  listener = Listener(on_release=on_release)
  listener.start()

def styleConfig():
  global theme
  if theme == 'arc':
    style.theme_use('equilux')
    theme = 'equilux'
  else:
    style.theme_use('arc')
    theme = 'arc'
  window.configure(bg=style.lookup('TLabel', 'background'))

def check(inStr, acttyp):
  if acttyp == '1':
    if not inStr.isdigit():
      return False
  return True

def close():
  listener.stop()
  macro.exit()
  window.destroy()

def setHotkey():
  global hotkeyButton
  answer = simpledialog.askstring( 'Set hotkey button',  'Please key in the button name')
  if answer == '':
    messagebox.showwarning('Invalid key', f'Invalid key "{answer}"')
  elif answer is None:
    pass
  elif hasattr(Key, answer.lower()):
    hotkeyButton = getattr(Key, answer.lower())
    startStopButton['text'] = f'Start/Stop ({answer.upper()})'
    listener.stop()
    initListener()
  elif len(answer) > 1:
    messagebox.showwarning('Invalid key', f'Invalid key "{answer}"')
  else:
    hotkeyButton = KeyCode(char=answer)
    startStopButton['text'] = f'Start/Stop ({answer})'
    listener.stop()
    initListener()

def getFilePath():
  global filePath
  path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[('csv files','*.csv')])
  if path in (None, ''):
    filePath = None
  else:
    filePath = path

def configure():
  if macro.status:
    macro.stop_macro()
  else:
    if filePath == None:
      messagebox.showwarning('Warning', 'Please select a file to run')
    elif mode.get() == 'preset':
      macro.start_macro(filePath, int(xTimes.get()))
    else:
      macro.start_macro(filePath, mode.get())

window.protocol('WM_DELETE_WINDOW', close)

settings = ttk.LabelFrame(window, text='Settings')
settings.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

modeOptions = ttk.LabelFrame(window, text='Modes')
modeOptions.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=1, pady=1)

mode = tk.StringVar(modeOptions, 'forever')
repeatAmt = tk.StringVar(modeOptions, '1')

buttonDict = {
  'Select File' : (settings, getFilePath, 0, 0),
  'Set hotkey button' : (settings, setHotkey, 1, 0),
  'Configure Theme' : (settings, styleConfig, 2, 0),
  'Exit' : (window, close, 2, 1)
}

radioButtonDict = {
  'Repeat until stopped' : ('forever', 0, 0, 2),
  'Repeat' : ('preset', 1, 0, 1),
  'Play once' : ('once', 2, 0, 2)
}

for text, args in buttonDict.items():
  ttk.Button(args[0], text=text, command=args[1]
  ).grid(row=args[2], column=args[3])

for text, args in radioButtonDict.items():
  ttk.Radiobutton(modeOptions, variable=mode, text=text, value=args[0]
  ).grid(row=args[1], column=args[2], columnspan=args[3], sticky='ew')

xTimes = ttk.Spinbox(modeOptions, textvariable=repeatAmt, validate='key', width=5, from_=1.0, to=float('inf'))
xTimes['validatecommand'] = (xTimes.register(check), '%P', '%d')
xTimes.grid(row=1, column=1)

ttk.Label(modeOptions, text='time(s)').grid(row=1, column=2)

startStopButton = ttk.Button(window, text='Start/Stop (F5)', command=configure)
startStopButton.grid(row=2, column=0)


macro = Controller()
macro.start()
initListener()
window.mainloop()