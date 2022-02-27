from micropi import Stepper
import time
import RPi.GPIO as GPIO

s1 = Stepper("STEPPER1")

# Rotate Stepper 2 Continuously in forward/backward direction

try:
    while True:
        s1.forward(0.01, 90)   # Delay and Steps
        #time.sleep(0.1)
        #s1.backward(0.01, 90)
        #time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
