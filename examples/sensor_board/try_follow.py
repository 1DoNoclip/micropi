import RPi.GPIO as GPIO
import time
from micropi import Motor, Sensor

m1 = Motor("MOTOR1")
m2 = Motor("MOTOR2")
ls1 = Sensor("IR1", 0)
ls2 = Sensor("IR2", 0)
while True:
  ls1.iRCheck()
  ls2.iRCheck()
  if ls1.Triggered == False and ls2.Triggered == False:
    m1.forward(40)
    m2.forward(40)
  elif ls1.Triggered == True and ls2.Triggered == False:
    m2.forward(40)
    m1.stop()
  elif ls1.Triggered == False and ls2.Triggered == True:
    m1.forward(40)
    m2.stop()
  else:
    m1.stop()
    m2.stop()

GPIO.cleanup()

