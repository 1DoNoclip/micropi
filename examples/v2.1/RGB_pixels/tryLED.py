from micropi import LED
from time import sleep

led = LED()

led.set_color(0,255,0,0)
sleep(1)
led.set_color(0,0,0,0)

led.set_color(1,0,255,0)
sleep(1)
led.set_color(1,0,0,0)

led.set_color(2,0,0,255)
sleep(1)
led.set_color(2,0,0,0)

led.set_color(3,255,255,255)
sleep(1)
led.set_color(3,0,0,0)

led.set_color(0,0,128,128)
sleep(1)
led.set_color(0,0,0,0)
