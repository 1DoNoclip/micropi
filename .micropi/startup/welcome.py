from micropi import OLED, Buzzer, LED
from time import sleep

def main():

    oled = OLED()
    buzzer =  Buzzer()
    led =  LED()

    oled.img()

    delay = 0.3

    led.set_color(0,255,0,0)
    buzzer.play("D",delay)
    sleep(delay)
    led.set_color(0,0,0,0)

    led.set_color(1,0,255,0)
    buzzer.play("E",delay)
    sleep(delay)
    led.set_color(1,0,0,0)

    led.set_color(2,0,0,255)
    buzzer.play("C",delay)
    sleep(delay)
    led.set_color(2,0,0,0)

    led.set_color(3,255,255,255)
    buzzer.play("c",delay)
    sleep(delay)
    led.set_color(3,0,0,0)

    led.set_color(0,0,128,128)
    buzzer.play("g",delay)
    sleep(delay)
    led.set_color(0,0,0,0)

if __name__ == "__main__":
    # execute only if run as a script
    main()
