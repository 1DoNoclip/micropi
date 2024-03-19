#!/usr/bin/python

# Library for MicroPi V2.1
# Developed by: SB Components & Hypersmart Ltd
# Project: MicroPi

# Modules
import RPi.GPIO as GPIO                     # RPi GPIO Library
from rpi_ws281x import PixelStrip, Color    # ws281x Library, may need to disable audio?
#import Adafruit_SSD1306                    # Adafruit SSD1306 LCD Display
from board import SCL, SDA
import busio
import adafruit_ssd1306
# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
from PIL import Image, ImageDraw, ImageFont # Pillow Image Library
import subprocess

from time import sleep, time
from threading import Thread # For buzzer to not yield thread

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Classes
class Motor:

    """Class to handle interaction with the motor pins

    Supports redefinition of "forward" and "backward" depending on how motors are connected:
    do this to ensure the object.forward(speed) and object.reverse(speed) work as intended
    Use the supplied Motorshieldtest module to test the correct configuration for your project.
    
    Arguments:
        motor = string motor pin label (i.e. "MOTOR1","MOTOR2","MOTOR3","MOTOR4") identifying the pins to which the motor is connected.
        
        config = int defines which pins control "forward" and "backward" movement
    
    You can access the motor's current direction by doing object.direction.

    You can access the motor's current speed by doing object.speed"""

    MOTOR_PINS = {
        "MOTOR4": {"e": 12, "f": 8, "r": 7},
        "MOTOR3": {"e": 21, "f": 9, "r": 11},
        "MOTOR2": {"e": 25, "f": 24, "r": 23},
        "MOTOR1": {"e": 17, "f": 27, "r": 22}
	}

    def __init__(self, motor: str):
        self.direction = "stopped" # Direction of motor
        self.speed = 0 # Speed of motor

        self.name = motor # For linked motors allows to access same name

        self.test_mode = False
        self.pins = self.MOTOR_PINS[motor]

        GPIO.setup(self.pins['e'], GPIO.OUT)
        GPIO.setup(self.pins['f'], GPIO.OUT)
        GPIO.setup(self.pins['r'], GPIO.OUT)

        # 50 Hz frequency
        self.PWM = GPIO.PWM(self.pins['e'], 50)
        self.PWM.start(0)
        GPIO.output(self.pins['e'], GPIO.HIGH)
        GPIO.output(self.pins['f'], GPIO.LOW)
        GPIO.output(self.pins['r'], GPIO.LOW)

    def set_test_mode(self, state: bool):
        """Puts the motor into test mode.
        When in test mode the Arrow associated with the motor receives power on "forward" rather than the motor.
        Useful when testing your code.

        Arguments:
            state: boolean --> True = test mode on, False = test mode off"""
        self.test_mode = state

    def forward(self, speed: int | float):
        """Starts the motor turning in its configured "forward" direction.

        Arguments:
            speed = Duty Cycle Percentage from 0 to 100.
            
            0 - stop and 100 - maximum speed"""

        if self.test_mode:
            print("arrow")
        else:
            if float(speed) is None: # Cannot convert number to float (ints will, other types like bool will not)
                raise TypeError("Must be int | float for speed")

            if speed > 0: # If speed is <= 0 then stop motor
                self.direction = "forward"
                self.speed = speed

                self.PWM.ChangeDutyCycle(speed)
                GPIO.output(self.pins['f'], GPIO.HIGH)
                GPIO.output(self.pins['r'], GPIO.LOW)
            else:
                self.stop()

    def reverse(self, speed: int | float):
        """Starts the motor turning in its configured "reverse" direction.

        Arguments:
            speed = Duty Cycle Percentage from 0 to 100.
            
            0 - stop and 100 - maximum speed"""

        if self.test_mode:
            print("Arrow")
        else:
            if float(speed) is None: # Cannot convert number to float (ints will, other types like bool will not)
                raise TypeError("Must be int | float for speed")

            if speed > 0: # If speed is <= 0 then stop motor
                self.direction = "reverse"
                self.speed = speed

                self.PWM.ChangeDutyCycle(speed)
                GPIO.output(self.pins['f'], GPIO.LOW)
                GPIO.output(self.pins['r'], GPIO.HIGH)
            else:
                self.stop()

    def stop(self):
        """Stops power to motor, takes no args"""

        self.direction = "stopped"
        self.speed = 0
        
        self.PWM.ChangeDutyCycle(0)
        GPIO.output(self.pins['f'], GPIO.LOW)
        GPIO.output(self.pins['r'], GPIO.LOW)

    def change_speed(self, new_speed: int | float):
        """Allows changing speed of motor without changing direction
        
        If motor is not moving, motor will move forward at new_speed"""

        self.speed = new_speed

        # If motor is not moving, just make it move forward at speed
        if self.direction == "forward" or self.direction == "stopped":
            self.direction = "forward" # If it was stopped before

            self.forward(new_speed)

        elif self.direction == "reverse":
            self.reverse(new_speed)


class LinkedMotors:

    """Links 2 or more motors together as a set.
    This allows a single command to be used to control a linked set of motors.
    e.g: For a 4WD vehicle this allows a single command to make all 4 wheels move.
    
    Arguments:
        *motors = a list of Motor objects"""
    
    def __init__(self, *motors: list[Motor]):
        self.motors = {}
        for motor in motors:
            motor: Motor
            motor_name = motor.name
            self.motors[motor_name] = motor # Append motor to dictionary
        
        self.number_of_motors = len(motors)
    
    def forward(self, speed: int | float):
        """Make all motors move forward at set speed"""
        for motor in self.motors: motor: Motor; motor.forward(speed)
    
    def reverse(self, speed: int | float):
        """Make al motors move in reverse at set speed"""
        for motor in self.motors: motor: Motor; motor.reverse(speed)
    
    def stop(self):
        """Stops power to all motors, takes no args"""
        for motor in self.motors: motor: Motor; motor.stop()
    
    def change_speed(self, new_speed: int | float):
        """Allows changing speed of motors without changing direction
        
        If motor is not moving, motor will move forward at new_speed"""
        for motor in self.motors: motor: Motor; motor.change_speed(new_speed)


class Stepper:

    """Defines stepper motor pins on the MotorShield

    Arguments:
        motor = stepper motor"""

    STEPPER_PINS = {"STEPPER1": {"en1": 21, "en2": 12, "c1": 9, "c2": 11, "c3": 8, "c4": 7},
                   "STEPPER2": {"en1": 17, "en2": 25, "c1": 27, "c2": 22, "c3": 24, "c4": 23}}

    def __init__(self, motor):
        self.config = self.STEPPER_PINS[motor]
        GPIO.setup(self.config["en1"], GPIO.OUT)
        GPIO.setup(self.config["en2"], GPIO.OUT)
        GPIO.setup(self.config["c1"], GPIO.OUT)
        GPIO.setup(self.config["c2"], GPIO.OUT)
        GPIO.setup(self.config["c3"], GPIO.OUT)
        GPIO.setup(self.config["c4"], GPIO.OUT)

        GPIO.output(self.config["en1"], GPIO.HIGH)
        GPIO.output(self.config["en2"], GPIO.HIGH)
        GPIO.output(self.config["c1"], GPIO.LOW)
        GPIO.output(self.config["c2"], GPIO.LOW)
        GPIO.output(self.config["c3"], GPIO.LOW)
        GPIO.output(self.config["c4"], GPIO.LOW)

    def set_step(self, w1, w2, w3, w4):
        """Set steps of Stepper Motor

        Arguments
            w1, w2, w3, w4 = Wire of Stepper Motor"""

        GPIO.output(self.config["c1"], w1)
        GPIO.output(self.config["c2"], w2)
        GPIO.output(self.config["c3"], w3)
        GPIO.output(self.config["c4"], w4)

    def forward(self, delay, steps: int):
        """Rotate Stepper motor in forward direction
        
        Arguments:
            delay: time between steps in miliseconds
            
            steps: Number of Steps"""

        for _ in range(0, steps):
            self.setStep(1, 0, 0, 0)
            sleep(delay)
            self.setStep(0, 1, 0, 0)
            sleep(delay)
            self.setStep(0, 0, 1, 0)
            sleep(delay)
            self.setStep(0, 0, 0, 1)
            sleep(delay)

    def backward(self, delay, steps):
        """Rotate Stepper motor in backward direction
        
        Arguments:
            delay: time between steps in miliseconds
            
            steps: Number of Steps"""

        for _ in range(0, steps):
            self.setStep(0, 0, 0, 1)
            sleep(delay)
            self.setStep(0, 0, 1, 0)
            sleep(delay)
            self.setStep(0, 1, 0, 0)
            sleep(delay)
            self.setStep(1, 0, 0, 0)
            sleep(delay)

    def stop(self):
        """Stops power to the motor, takes no args"""

        GPIO.output(self.config['c1'], GPIO.LOW)
        GPIO.output(self.config['c2'], GPIO.LOW)
        GPIO.output(self.config['c3'], GPIO.LOW)
        GPIO.output(self.config['c4'], GPIO.LOW)


class Sensor:

    """Defines a sensor connected to the sensor pins on the MotorShield
    
    Arguments:
        sensor_type: string identifying which sensor is being configured.
        i.e. "IR1", "IR2", "ULTRASONIC"

        boundary: integer specifying the minimum distance at which the sensor will return a
        triggered response of True. Must be number between 1 and 10 inclusive."""

    triggered = False

    def __init__(self, sensor_type, boundary):
        self.config = self.SENSOR_PINS[sensor_type]
        self.boundary = boundary
        self.last_read = 0
        if "trigger" in self.config:
            GPIO.setup(self.config["trigger"], GPIO.OUT)
        GPIO.setup(self.config["echo"], GPIO.IN)

    def IR_check(self) -> bool:
        """Will set self's triggered value to True or False and return triggered's value too"""
        input_state = GPIO.input(self.config["echo"])
        if input_state == 1:
            self.triggered = True
            return self.triggered
        else:
            self.triggered = False
            return self.triggered

    def sonic_check(self):
        """Will set self's triggered value to True or False and return triggered and distance value too"""
        sleep(0.333)
        GPIO.output(self.config["trigger"], True)
        sleep(0.00001)
        GPIO.output(self.config["trigger"], False)

        start = time()

        while GPIO.input(self.config["echo"]) == 0:
            start = time()

        while GPIO.input(self.config["echo"]) == 1:
            stop = time()

        elapsed = stop - start
        measure = (elapsed * 34300) / 2
        self.last_read = measure

        if self.boundary > measure:
            self.triggered = True
            return self.triggered, measure
        else:
            self.triggered = False
            return self.triggered, measure
    
    SENSOR_PINS = {
        "IR1": {"echo": 4,"check": IR_check},
        "IR2": {"echo": 18, "check": IR_check},
        "ULTRASONIC": {"trigger": 5, "echo": 6, "check": sonic_check},
    }

    def trigger(self) -> bool:
        """Executes the relevant routine that activates and takes a
        reading from the specified sensor.
        If the specified "boundary" has been breached, the Sensor's
        triggered attribute gets set to True."""

        self.config["check"](self)
        return self.triggered


class Buzzer:

    NOTES = {
        "a": 220, "a#": 233, "b": 247, "c": 262, "c#": 277, "d": 294,
        "d#": 311, "e": 330, "f": 349, "f#": 370, "g": 392, "g#": 415,
        "A": 440, "A#": 466, "B": 494, "C": 523, "C#": 554, "D": 587,
        "D#": 622, "E": 659, "F": 698, "F#": 740, "G": 784, "G#": 831
    }

    def __init__(self):
        self.buzzerPIN = 16
        GPIO.setup(self.buzzerPIN, GPIO.OUT)

    @classmethod
    def __play(cls, frequency: int, duration):
        """Will play frequency for duration, and yield thread until done
        
        Not recommended to use this method as play_frequency() and play_note() run in coroutines"""

        buzzer = GPIO.PWM(cls.buzzerPIN, 1000) # Buzzer initialization to 1KHz
        buzzer.start(10) # Set duty cycle to 10
        buzzer.ChangeFrequency(frequency)
        sleep(duration) # Will not yield whatever calls it
        buzzer.stop()
    
    @classmethod
    def play_frequency(cls, frequency: int, duration):
        """See https://demos.ca/notefreqs (262 piano middle c)

        Will play frequency for duration on buzzer. Frequency can be int.
        Duration will be handled by time.sleep(duration)

        Note: Function runs in coroutine so will not yield main thread
        """
        
        task = Thread(target=cls.__play, args=(frequency, duration,))
        task.start()
    
    @classmethod
    def play_note(cls, note: str, duration):
        """See https://demos.ca/notefreqs (262 piano middle c)

        Will play note for duration on buzzer. Note can be picked from list of notes by doing
        object.NOTES or object.get_notes() to return a dict of all notes and their frequency.
        
        This method converts your note to the frequency and calls the play_tone() method
        Duration will be handled by time.sleep(duration)

        Note: Function runs in coroutine so will not yield main thread
        """

        frequency = cls.NOTES[note]
        cls.play_tone(frequency, duration) # This will call play_tone() as that already has logic for thread

    # A bit useless as person could just get attribute instead
    @classmethod
    def get_notes(cls): return cls.NOTES


class IR_Detect:

    BUTTON_VALS = {
        0x45: "1", 0x46: "2", 0x47: "3",
        0x44: "4", 0x40: "5", 0x43: "6",
        0x07: "7", 0x15: "8", 0x09: "9",
        0x19: "0", 0x16: "*", 0x0d: "#",

        0x18: "Up", 0x52: "Down",
        0x08: "Left", 0x5a: "Right",
        0x1c: "OK",
	}

    IR_PIN = 20

    @classmethod
    def __init__(cls):
        GPIO.setup(cls.IR_PIN, GPIO.IN, GPIO.PUD_UP)
    
    @classmethod
    def get_button_vals(cls):
        return cls.BUTTON_VALS

    @classmethod
    def read(cls):
        """Returns which button has been pressed if a button has been pressed"""

        if GPIO.input(cls.IR_PIN) == 0:
            count = 0
            while GPIO.input(cls.IR_PIN) == 0 and count < 200:
                count += 1
                sleep(0.00006)
            count = 0
            while GPIO.input(cls.IR_PIN) == 1 and count < 80:
                count += 1
                sleep(0.00006)
            idx = 0
            cnt = 0
            data = [0,0,0,0]
            for _ in range(0,32):
                count = 0
                while GPIO.input(cls.IR_PIN) == 0 and count < 15:
                    count += 1
                    sleep(0.00006)
                count = 0
                while GPIO.input(cls.IR_PIN) == 1 and count < 40:
                    count += 1
                    sleep(0.00006)
                if count > 8:
                    data[idx] |= 1<<cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1

            if (data[0] + data[1] == 0xFF) and (data[2] + data[3] == 0xFF):
                # print("Get the key: 0x%02x" %data[2])

                return cls.BUTTON_VALS[data[2]]


class LED:

    def __init__(self, LED_number: str):
        """Creates object to interract with LED with specified number
        
        Arguments:
            LED_number: string in the format "LED{number}" where number is an int between 0 and 3 inclusive"""

        # LED Strip configuration:
        # Number of LED pixels
        LED_COUNT = 4
        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0)
        LED_PIN = 10
        # LED signal frequency in hertz (usually 800khz)
        LED_FREQ_HZ = 800000
        # DMA channel to use for generating signal (try 10)
        LED_DMA = 10
        # Set to 0 for darkest and 255 for brightest
        LED_BRIGHTNESS = 100
        # True to invert the signal (when using NPN transistor level shift)
        LED_INVERT = False
        # set to '1' for GPIOs 13. 19, 41, 45 or 53
        LED_CHANNEL = 0
        # Create NeoPixel object with appropriate configuration.

        ### INEFFICIENT because I do not know PixelStrip so every LED object creates for every LED, but you can only control the one you have specified
        self.strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        # Describes LED number:
        if type(LED_number) != int:
            raise TypeError("Wrong type for LED_number, must be an int")
        
        if LED_number in range(0, 3 + 1):
            self.LED_number = LED_number
        else:
            raise ValueError("Out-of-range for LED_number, must be 0-4 inclusive")

    def set_color(self, red: int, green: int, blue: int):
        """
        Sets the color for the LED.

        Args:
            red: int -> number between 0 and 255 inclusive
            green: int -> number between 0 and 255 inclusive
            blue: int -> number between 0 and 255 inclusive

        Raises:
            ValueError: If any value is outside the 0-255 range.
        """

        
        # Validate color values
        for value in (red, green, blue):
            if not (value in range(0, 255 + 1)):
                raise ValueError("Color values must be between 0 and 255")

        def get_bit_number(value):
            if value <= 0:
                return 0
            
            power = 128
            bit = 7
            while value < power:
                # //= not supported in Python
                power = power // 2
                bit -= 1

            return bit
        
        VALUES = [0, 5, 25, 45, 65, 85, 105, 125]
        R = VALUES[get_bit_number(red % 256)]
        G = VALUES[get_bit_number(green % 256)]
        B = VALUES[get_bit_number(blue % 256)]

        self.strip.setPixelColor(self.LED_number % 4, Color(R, G, B))
        self.strip.show()
    
    def off(self):
        """Turns the LED off"""

        self.strip.setPixelColor(self.LED_number % 4, Color(0, 0, 0))
        self.strip.show()


class OLED:

    def __init__(self):
        #self.disp32 = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        #self.disp64 = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        self.line = ["","","",""]
        pass

    def print_stats(self):
        self.disp32 = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        # Clear display.
        self.disp32.fill(0)
        self.disp32.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width = self.disp32.width
        height = self.disp32.height
        #print(self.disp32.height)
        self.image = Image.new("1", (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        top = -2 # Padding
        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0

        # Load default font.
        font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        #self.setline(0,IP)
        cmd = 'cut -f 1 -d " " /proc/loadavg'
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        #self.setline(1,CPU)
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        #self.setline(2,MemUsage)
        Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        #self.setline(3,Disk)

        IP = "IP:" + self.get_ip_address() # Keep checking for IP Address to appear

        self.draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
        self.draw.text((x, top + 8), "CPU load: " + CPU, font=font, fill=255)
        self.draw.text((x, top + 16), MemUsage, font=font, fill=255)
        self.draw.text((x, top + 25), Disk, font=font, fill=255)

        # Display image.
        self.disp32.image(self.image)
        self.disp32.show()
        sleep(0.1)

    def get_ip_address(self):
        """Returns current IP address"""

        ip: str = "0.0.0.0"
        while len(ip) < 8:
            cmd = "hostname -I"
            ip = subprocess.check_output(cmd, shell=True).decode('ASCII')
        return ip

    def print(self, line, str):
        self.disp32 = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
        # Clear display.
        self.disp32.fill(0)
        self.disp32.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        width, height = self.disp32.width, self.disp32.height
        self.image = Image.new("1", (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        top = -2 # Padding

        # Move left to right keeping track of the current x position for drawing shapes.
        x = 0

        # Load default font.
        font = ImageFont.load_default()

        # Alternatively load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        # font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if line == 1:
            self.draw.text((x, top + 0), str, font=font, fill=255)
        if line == 2:
            self.draw.text((x, top + 8), str, font=font, fill=255)
        if line == 3:
            self.draw.text((x, top + 16), str, font=font, fill=255)
        if line == 4:
            self.draw.text((x, top + 25), str, font=font, fill=255)

        self.disp32.image(self.image)
        self.disp32.show()
        sleep(0.1)

    def img(self):
            self.disp64 = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
            # Clear display.
            self.disp64.fill(0)
            self.disp64.show()

            # Load image based on OLED display height.  Note that image is converted to 1 bit color.
            #print(self.disp64.height)
            self.image = Image.open("/home/pi/micropi/images/micropi_oled_64.ppm").convert("1")
                
            # Display image.
            self.disp64.image(self.image)
            self.disp64.show()

    def __del__(self):
        # GPIO.cleanup()
        pass


class Button:

    def __init__(self, button_number: str):
        """button_number must be "BUTTON1" or "BUTTON2" """
        # GPIO.setmode(GPIO.BCM)
        if button_number == "BUTTON1":
            self.pb = 26
        elif button_number == "BUTTON2":
            self.pb = 19
        else:
            raise ValueError("button_number must be 'BUTTON1' or 'BUTTON2'")
        
        self.pressed: bool = self.check_if_pressed()

        # Set pin 26 and 19 to be an input pin and
        # Set initial value to be pulled down
        GPIO.setup(self.pb, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def set_callback(self, button):
        # Setup event on pin 37 and 35 rising edge
        GPIO.add_event_detect(self.pb, GPIO.RISING, callback=button)

    def check_if_pressed(self) -> bool:
        self.pressed = GPIO.input(self.pb) == 0
        return self.pressed

    # def __del__(self):
        # GPIO.cleanup()
        # pass

# Main
if __name__ == "__main__":
    print("Welcome to the MicroPI library")

    if input("Do you want to test features? (y/n) ").lower() == "y":
        if input("Do you want to test motors? (y/n) ").lower() == "y":
            m1 = Motor("MOTOR1")
            m2 = Motor("MOTOR2")
            m1.forward(100)
            m2.forward(100)
            sleep(1)
            m1.stop()
            m2.stop()
        
        if input("Do you want to test buzzer? (y/n) ").lower() == "y":
            buzzer = Buzzer()
            notes = buzzer.NOTES
            # notes = buzzer.get_notes() works the same
            for note in notes:
                buzzer.play_note(note, 0.1)
                sleep(0.1)
        
        if input("Do you want to test LEDs? (y/n) ").lower() == "y":
            leds = {
                "LED0": LED(0),
                "LED1": LED(1),
                "LED2": LED(2),
                "LED3": LED(3),
            }

            count = 50
            for led in leds:
                led: LED # So methods appear
                led.set_color(count, count, count)
                count += 50
                sleep(0.5)

            sleep(1)

            for led in leds:
                led: LED # So methods appear
                led.set_color(0, 0, 0)
        
        if input("Do you want to test OLED? (y/n) ").lower() == "y":
            oled = OLED()
            for line in range(1, 4 + 1):
                oled.print(line, f"Testing line {str(line)}")
                sleep(0.25)
            
            sleep(1)

            oled.print_stats()
        
        if input("Do you want to test buttons? (y/n) ").lower() == "y":
            buttons = {
                "BUTTON1": Button("BUTTON1"),
                "BUTTON2": Button("BUTTON2"),
            }

            for _ in range(10):
                # check_if_pressed() returns triggered value, you can also do:
                # buttons['BUTTON1'].check_if_pressed()
                # if buttons['BUTTON1'].triggered: ...

                if buttons["BUTTON1"].check_if_pressed():
                    print("BUTTON1 pressed")
                else:
                    print("BUTTON1 not pressed")
                
                if buttons["BUTTON2"].check_if_pressed():
                    print("BUTTON2 pressed")
                else:
                    print("BUTTON2 not pressed")
                
                sleep(0.5)
