import RPi.GPIO as GPIO
import time
from micropi import Sensor

distance = Sensor("ULTRASONIC", 10)

while True:
    distance.sonicCheck()
    if(distance.Triggered):
        print("obtruction detected")
        
#Reset ports used by motor program back to input mode
GPIO.cleanup()
    
