from micropi import Motor
from time import sleep
# import RPi.GPIO as GPIO

m1 = Motor("MOTOR1")
m2 = Motor("MOTOR2")

m1.forward(60)
m2.forward(60)
sleep(3)
m1.stop()
m2.stop()
sleep(1)
m1.reverse(50)
m2.reverse(50)
sleep(3)
m1.stop()
m2.stop()
#Reset ports used by motor program back to input mode
# GPIO.cleanup()




