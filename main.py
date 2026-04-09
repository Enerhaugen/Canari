import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd
import time
import pwmio
import analogio
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C

reset_pin = None
i2c = busio.I2C(board.GP7, board.GP6, frequency=100000)
# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)
airquality = pm25.read()

#Deefines microphone
mic = analogio.AnalogIn(board.GP27)
#Variables to measure sound
low_sound = 0
high_sound = 0

#Defines the LCD screen
lcd_rs = digitalio.DigitalInOut(board.GP28)
lcd_e = digitalio.DigitalInOut(board.GP16)
lcd_db4 = digitalio.DigitalInOut(board.GP26)
lcd_db5 = digitalio.DigitalInOut(board.GP22)
lcd_db6 = digitalio.DigitalInOut(board.GP21)
lcd_db7 = digitalio.DigitalInOut(board.GP20)
lcd_columns = 16
lcd_rows = 2
lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_e, lcd_db4, lcd_db5, lcd_db6, lcd_db7, lcd_columns, lcd_rows)

#Defines Vibration Sensor
vibration = digitalio.DigitalInOut(board.GP0) #Vibration is defined as the input from slot GP16 in the Raspberry Pi Pico.
vibration.direction = digitalio.Direction.INPUT
vibration_count = 0
no_vibration_count = 0
timer_vibration = time.monotonic() #Time monotonic returns seconds in float.
timer_sound = time.monotonic()
timer_air = time.monotonic()
#Defines LED
led = digitalio.DigitalInOut(board.GP19)
led.direction = digitalio.Direction.OUTPUT

#Defines buzzer
buzzer = pwmio.PWMOut(board.GP18, variable_frequency=True)
OFF = 0
ON = 2**15


def warning_on():
    buzzer.duty_cycle = ON
    led.value = True
    led.value = True
    time.sleep(5)

def warning_off():
    lcd.clear()#Clears the LCD Screen
    buzzer.duty_cycle = OFF #turns of speaker
    led.value = False #Turns off led warning light
    

while True:
    time.sleep(0.5)
    try:
        airquality = pm25.read()
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue
    
    airquality_pm10 = airquality["pm10 env"]
    airquality_pm25 = airquality["pm25 env"]
    airquality_pm100 = airquality["pm100 env"]
    
    if airquality_pm10 > 2:
        warning_on()
        print("PM10 AQ")
        time.sleep(5)
        warning_off()
        
    elif airquality_pm25 > 5:
        warning_on()
        print("PM25 AQ")
        time.sleep(5)
        warning_off()
    elif airquality_pm100 > 10:
        warning_on()
        print("PM100 AQ")
        time.sleep(5)
        warning_off()
        
        
    if vibration.value == True:
        vibration_count += 1#Adds 1 to the vibration_count value to be used when the time is up.
        print("Vibration Detected!", vibration_count, "\n #############") #Prints if the sensor detects a vibration
        time.sleep(0.5) 
        
        
    else:
        no_vibration_count += 1 #Adds a one to the no_vibartion_count variable when no vibrations are detected.
        print("No Vibration Detected.", no_vibration_count,  "\n #############") #Prints when no vibrations are detected by the sensor.
    
    
    
    
     #Defines the vibration warnings.   
    if vibration_count >=10:
        print("Warning, Vibration")
        lcd.message("Too much vibration! \n Take a Break!")
        warning_on()
        warning_off()
        vibration_count = 0
        no_vibration_count = 0
        
    elif no_vibration_count >= 10:
        print("ikke for mye vibrasjon.")
        vibration_count = 0
        no_vibration_count = 0
            
        
    if mic.value > 40000:
        high_sound += 1
        print("Høy lyd!", high_sound, "\n ###################")
    else:
        low_sound += 1
        print("lav lyd.", low_sound, "\n ###################")
    
    if high_sound >= 10:
        print("For høy lyd!")
        warning_on()
        lcd.message("Loud Enviroment, \n Please wear safety gear")
        warning_off()
        high_sound = 0
    if low_sound >= 10:
        print("Ikke for lav lyd")
        high_sound = 0
        low_sound = 0
    
