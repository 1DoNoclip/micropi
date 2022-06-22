from micropi import Motor, Sensor
import time
import RPi.GPIO as GPIO

m1 = Motor("MOTOR1")
m2 = Motor("MOTOR2")
distance = Sensor("ULTRASONIC", 10)

while True:
    m1.forward(60)
    m2.forward(60)
    distance.sonicCheck()
    if(distance.Triggered):
        print("obtruction detected")
        m1.stop()
        m2.stop()
        time.sleep(1)
        m1.reverse(50)
        m2.reverse(50)
        time.sleep(1)
        m1.stop()
        m2.stop()
        time.sleep(1)
        m1.forward(60)
        time.sleep(1)
#Reset ports used by motor program back to input mode
GPIO.cleanup()
