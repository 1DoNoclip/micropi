import RPi.GPIO as GPIO 

GPIO.setmode(GPIO.BCM)

audioPIN = 13
GPIO.setup(audioPIN, GPIO.OUT)
GPIO.output(audioPIN, GPIO.HIGH)

#Reset ports used by motor program back to input mode
GPIO.cleanup()