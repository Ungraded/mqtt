#!/usr/bin/python3

import tkinter as tk
import tkinter.ttk as ttk
import atexit
import datetime
import sqlite3
import globalvar

global configuration_event
configuration_event = ''

# item detail window
def detail_window(curItem):
	print(curItem)
	print(curItem['values'])

	#win = tk.Toplevel(width=250, height=140, bd=2, relief='sunken')
	win = tk.Toplevel(width=250, height=130)
	win.wm_title("Coordinate detail")
	win.resizable(width=0, height=0)
	win.columnconfigure(0, weight=1)
	win.columnconfigure(1, weight=1)

	timeLabel = tk.Label(win, text="Time:")
	timeLabel.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
	timeValue = tk.Label(win, text=curItem['text'])
	timeValue.grid(row=0, column=1, sticky=tk.E, padx=10)

	curValues = curItem['values']

	xLabel = tk.Label(win, text="x:")
	xLabel.grid(row=1, column=0, sticky=tk.W, padx=10)
	xValue = tk.Label(win, text=curValues[0])
	xValue.grid(row=1, column=1, sticky=tk.E, padx=10)

	yLabel = tk.Label(win, text="y:")
	yLabel.grid(row=2, column=0, sticky=tk.W, padx=10)
	yValue = tk.Label(win, text=curValues[1])
	yValue.grid(row=2, column=1, sticky=tk.E, padx=10)

	zLabel = tk.Label(win, text="z:")
	zLabel.grid(row=3, column=0, sticky=tk.W, padx=10)
	zValue = tk.Label(win, text=curValues[2])
	zValue.grid(row=3, column=1, sticky=tk.E, padx=10)

	closeButton = ttk.Button(win, text="Close", command=win.destroy)
	closeButton.grid(row=4, column=0, sticky=tk.W + tk.E, padx=10, pady=5)

# read last saved geometry
def read_config():
	global xPrevious
	global yPrevious

	dbConnector = sqlite3.connect(globalvar.mqttdb)
	appConfig = (None, '', '', '', '', '')
	dbCursor = dbConnector.cursor()
	dbCursor.execute('SELECT * FROM configuration WHERE id=1')
	appConfig = dbCursor.fetchone()
	dbConnector.close()
	print('read geometry: ' + str(appConfig))

	if appConfig[2] == '':
		ret2 = '200'
	else:
		ret2 = appConfig[2]

	if appConfig[3] == '':
		ret3 = '200'
	else:
		ret3 = appConfig[3]

	if appConfig[4] == '':
		ret4 = '50'
	else:
		ret4 = appConfig[4]

	if appConfig[5] == '':
		ret5 = '50'
	else:
		ret5 = appConfig[5]

	xPrevious = int(ret4)
	yPrevious = int(ret5)

	if int(ret4) >= 0:
		ret4 = '+' + ret4

	if int(ret5) >= 0:
		ret5 = '+' + ret5

	return (ret2 + 'x' + ret3 + ret4 + ret5)

# save current geometry
def write_config():
	global configuration_event
	global xPrevious
	global yPrevious
	ce = configuration_event
	print('ce:' + ce)

	if ce == '':
		print('return')
		return

	#  <Configure event x=152 y=132 width=76 height=25>
	wIndex = ce.find('width=') + 6
	wIndexEnd = ce.find(' ', wIndex)
	width = ce[wIndex:wIndexEnd]
	
	hIndex = ce.find('height=') + 7
	hIndexEnd = ce.find('>', hIndex)
	height = ce[hIndex:hIndexEnd]
	
	xIndex = ce.find('x=') + 2
	xIndexEnd = ce.find(' ', xIndex)
	xP = ce[xIndex:xIndexEnd]
	if int(xP) == 0:
		xP = str(xPrevious)
	
	yIndex = ce.find('y=') + 2
	yIndexEnd = ce.find(' ', yIndex)
	yP = ce[yIndex:yIndexEnd]
	if int(yP) == 0:
		yP = str(yPrevious)

	timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
	data = (timestamp, width, height, xP, yP)

	dbConnector = sqlite3.connect(globalvar.mqttdb)
	dbCursor = dbConnector.cursor()
	dbCursor.execute('UPDATE configuration SET timestamp=?, width=?, height=?, positionX=?, positionY=? WHERE id=1', data)
	appConfig = dbCursor.fetchone()
	dbConnector.commit()
	dbConnector.close()
	print('configuration wrote:' + str(data))

def configureGeometry(geometry_event):
	global configuration_event
	global xPrevious
	global yPrevious
	configuration_event = str(geometry_event)
	ce = configuration_event

	xIndex = ce.find('x=') + 2
	xIndexEnd = ce.find(' ', xIndex)
	xP = ce[xIndex:xIndexEnd]
	if int(xP) != 0:
		xPrevious = int(xP)
	
	yIndex = ce.find('y=') + 2
	yIndexEnd = ce.find(' ', yIndex)
	yP = ce[yIndex:yIndexEnd]
	if int(yP) != 0:
		yPrevious = int(yP)

class App(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent=parent
		#self.place(x=10, y=10)
		self.initialize_user_interface()
		self.insert_data()

	# intializing UI
	def initialize_user_interface(self):
		self.parent.title("Coordinate viewer")
		self.parent.geometry(read_config())
		self.parent.grid_rowconfigure(0, weight=1)
		self.parent.grid_columnconfigure(0, weight=1)
		#self.parent.config(background="white", bd=2, relief="sunken")
		self.parent.config(background="white")

		self.tree = ttk.Treeview(self.parent, columns=('time', 'x', 'y', 'z'), selectmode='browse')
		#self.tree.pack(side='left')
		ysb = ttk.Scrollbar(self.parent, orient='vertical', command=self.tree.yview)
		xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
		self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)
		self.tree.heading('#0', text='Time')
		self.tree.heading('#1', text='x')
		self.tree.heading('#2', text='y')
		self.tree.heading('#3', text='z')
		self.tree.column('#1', width=40, anchor=tk.E, stretch=tk.NO)
		self.tree.column('#2', width=40, anchor=tk.E, stretch=tk.NO)
		self.tree.column('#3', width=40, anchor=tk.E, stretch=tk.NO)
		self.tree.column('#0', width=160, anchor=tk.W, stretch=tk.NO)
		
		self.tree.bind("<Double-1>", self.OnDoubleClick)
		
		self.tree.grid(row=4, columnspan=1, sticky='nsew')
		self.tree.grid(row=0, column=0)
		self.treeview = self.tree

		ysb.grid(row=0, column=4, sticky='ns')
		#xsb.grid(row=1, column=0, sticky='ew')
		
		#self.update_idletasks()

	# reading data from database and inserting it into treeview
	def insert_data(self):
		dbConnector = sqlite3.connect(globalvar.mqttdb)

		for row in dbConnector.execute('SELECT * FROM acceleration ORDER BY timestamp'):
			self.treeview.insert('', 'end', \
				text=row[1].replace('T', ' '), \
				values=(str(row[2]) + ' ' + str(row[3]) + ' ' + str(row[4])))

		dbConnector.close()

	# open item detail window on doubleclick
	def OnDoubleClick(self, event):
		item = self.tree.identify('item',event.x,event.y)
		#item = self.tree.selection()[0]
		#print("Clicked on", self.tree.item(item,"text"))
		curIndex = self.tree.focus()
		curItem = self.tree.item(curIndex)
		detail_window(curItem)

def main():
	atexit.register(write_config)
	root=tk.Tk()
	#root.bind('<Configure>', configureGeometry)
	root.minsize(width=295, height=100)
	root.resizable(width=0, height=1)
	go=App(root)
	root.bind('<Configure>', configureGeometry)
	#detail_window()
	root.mainloop()

# ----

if __name__=="__main__":
	main()