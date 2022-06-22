from micropi import Buttons
from time import sleep

pb2 = Buttons()

while True:
    print(pb2.isPB2Pressed())
    sleep(0.2)
