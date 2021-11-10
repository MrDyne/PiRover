# python 3.5
import asyncio
import json
import websockets
import RPi.GPIO as GPIO
import serial
import os

# connect to USB servo controller over serial
tty = serial.Serial('/dev/ttyACM0')

# setup RPi GPIO & define pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

# set motor states
def motor_state(e0,m0,e1,m1):
	GPIO.output(26, e0)
	GPIO.output(19, m0)
	GPIO.output(5, e1)
	GPIO.output(6, m1)

# camera
pan = 110
tilt = 75
cam_center = 75

# stuff
lights = False # lights are normal due to NPN transistor
laser = True # laser is backwards due to PNP transistor
GPIO.output(23, False)
GPIO.output(24, True)

def camera(p,t):
	global pan
	global tilt
	pan = max(0, min(pan + p, 254))
	tilt = max(0, min(tilt + t, 254))
	tty.write(bytearray([255,0,pan,255,1,tilt]))

def center():
	global pan
	global tilt
	pan = 110
	tilt = cam_center
	tty.write(bytearray([255,0,pan,255,1,tilt]))

# stop
motor_state(0,0,0,0)

# handle messages
@asyncio.coroutine
def remote_control(websocket, path):
	while True:
		message = yield from websocket.recv()
		data = json.loads(message)
		if data['action'] == "laser":
			print("LASER")
			global laser
			laser = not laser
			GPIO.output(24, laser)
		if data['action'] == "lights":
			print("LIGHTS")
			global lights
			lights = not lights
			GPIO.output(23, lights)
		if data['action'] == "speak":
			print("SPEAK")
			speak = "espeak '{0}' 2>/dev/null".format(data['text'])
			os.system(speak)
		if data['action'] == "stop":
			print("STOP")
			motor_state(0,0,0,0)
		if data['action'] == "move":
			if data['dir'] == 7:
				print("LEFT FORWARD TURN")
				motor_state(0,0,1,0)
			if data['dir'] == 8:
				print("FORWARD")
				motor_state(1,1,1,0)
			if data['dir'] == 9:
				print("RIGHT FORWARD TURN")
				motor_state(1,1,0,0)
			if data['dir'] == 4:
				print("COUNTER TURN")
				motor_state(1,0,1,0)
			if data['dir'] == 6:
				print("CLOCK TURN")
				motor_state(1,1,1,1)
			if data['dir'] == 1:
				print("LEFT BACKWARD TURN")
				motor_state(0,0,1,1)
			if data['dir'] == 2:
				print("REVERSE")
				motor_state(1,0,1,1)
			if data['dir'] == 3:
				print("RIGHT BACKWARD TURN")
				motor_state(1,0,0,0)
		if data["action"] == "cam":
			if data['dir'] == 5:
				center()
				print("Center")
			if data['dir'] == 7:
				camera(10,-10)
				print(" 1, -1")
			if data['dir'] == 8:
				camera(0,-10)
				print(" 0, -1")
			if data['dir'] == 9:
				camera(-10,-10)
				print("-1, -1")
			if data['dir'] == 4:
				camera(10,0)
				print(" 1,  0")
			if data['dir'] == 6:
				camera(-10,0)
				print("-1,  0")
			if data['dir'] == 1:
				camera(10,10)
				print(" 1,  1")
			if data['dir'] == 2:
				camera(0,10)
				print(" 0,  1")
			if data['dir'] == 3:
				camera(-10,10)
				print("-1,  1")

# start websocket server
start_server = websockets.serve(remote_control, '', 8081)

# run forever
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
