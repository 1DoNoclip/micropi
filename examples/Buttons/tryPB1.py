from micropi import Buttons
from time import sleep

pb1 = Buttons()

while True:
    print(pb1.isPB1Pressed())
    sleep(0.2)
