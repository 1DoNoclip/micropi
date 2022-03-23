import RPi.GPIO as GPIO 
import time
import subprocess

GPIO.setmode(GPIO.BCM)

audioPIN = 13
GPIO.setup(audioPIN, GPIO.OUT)

GPIO.output(audioPIN, GPIO.HIGH)
print("Audio PIN is now switched on")

subprocess.run(['aplay', '/home/pi/Music/sample1.wav'], timeout=10)

GPIO.output(audioPIN, GPIO.LOW)
print("Audio PIN is now switched off")

#Reset ports used by motor program back to input mode
GPIO.cleanup()

