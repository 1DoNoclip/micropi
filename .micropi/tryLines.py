import time
from micropi import Sensor

ls1 = Sensor("IR1",0)
ls2 = Sensor("IR2",0)

while True:
    ls1.iRCheck()
    ls2.iRCheck()
    if(ls1.Triggered):
        print("ls1 detected black line")
    if(ls2.Triggered):
        print("ls2 detected black line")
    time.sleep(0.5)

#Reset ports used by motor program back to input mode
GPIO.cleanup()
