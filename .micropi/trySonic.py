import RPi.GPIO as GPIO
import time
from micropi import Sensor

us = Sensor("ULTRASONIC", 10)

while True:
    us.sonicCheck()
    if(us.Triggered):
        print("obtruction detected")
        
#Reset ports used by motor program back to input mode
GPIO.cleanup()
    
