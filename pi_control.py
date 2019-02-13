import asyncio
import websockets
import RPi.GPIO as GPIO
import serial

# connect to USB servo controller over serial
tty = serial.Serial('/dev/ttyACM0')

# setup RPi GPIO & define pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)

# set motor states
def motor_state(e0,m0,e1,m1):
	GPIO.output(26, e0)
	GPIO.output(19, m0)
	GPIO.output(5, e1)
	GPIO.output(6, m1)

# stop
motor_state(0,0,0,0)

# handle messages
@asyncio.coroutine
def remote_control(websocket, path):
	while True:
		message = yield from websocket.recv()
		data = message.split(',')
		drive = int(data[0])
		pan = int(data[1])
		tilt = int(data[2])
		tty.write(bytearray([255,0,pan,255,1,tilt]))
		print(pan)
		print(tilt)
		if drive == 0:
			print("STOP")
			motor_state(0,0,0,0)
		elif drive == 1:
			print("FORWARD")
			motor_state(1,1,1,0)
		elif drive == 2:
			print("LEFT FORWARD TURN")
			motor_state(0,0,1,0)
		elif drive == 3:
			print("RIGHT FORWARD TURN")
			motor_state(1,1,0,0)
		elif drive == 4:
			print("COUNTER TURN")
			motor_state(1,0,1,0)
		elif drive == 5:
			print("CLOCK TURN")
			motor_state(1,1,1,1)
		elif drive == 6:
			print("LEFT BACKWARD TURN")
			motor_state(0,0,1,1)
		elif drive == 7:
			print("RIGHT BACKWARD TURN")
			motor_state(1,0,0,0)
		elif drive == 8:
			print("REVERSE")
			motor_state(1,0,1,1)

# start websocket server
start_server = websockets.serve(remote_control, '', 8081)

# run forever
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
