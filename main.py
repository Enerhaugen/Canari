import socketpool
import wifi
from adafruit_httpserver import Request, Response, Server, POST
import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd
import time
import pwmio
import analogio
from adafruit_pm25.i2c import PM25_I2C
import busio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from i2cdisplaybus import I2CDisplayBus
import displayio
import terminalio

#Piezo Buzzer
buzzer = pwmio.PWMOut(board.GP18, variable_frequency=True) #Defined buzzer, using guide: https://learn.adafruit.com/using-piezo-buzzers-with-circuitpython-arduino/circuitpython
buzzer.frequency = 440
OFF = 0
ON = 2**15

#LED Diode
led = digitalio.DigitalInOut(board.GP21) #Defined LED using guide: https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs/digital-outputs
led.direction = digitalio.Direction.OUTPUT


def warning_on():
    buzzer.duty_cycle = ON
    led.value = True

def warning_off():
    buzzer.duty_cycle = OFF
    led.value = False

#OLED

displayio.release_displays()

oled_reset = None

i2c = busio.I2C(board.GP1, board.GP0, frequency=100000) 

display_bus = I2CDisplayBus(i2c, device_address=0x3C, reset=oled_reset)

WIDTH = 128
HEIGHT = 32  
BORDER = 5

display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

splash = displayio.Group()
display.root_group = splash
display.sleep()

def warning_oled_text(message):
    text = message
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=HEIGHT // 5)
    splash.append(text_area)
    display.wake()
    return text

#Server
    
    
AP_SSID = "..."
AP_PASSWORD = "12345678"

print("Creating access point...")
wifi.radio.start_ap(ssid=AP_SSID, password=AP_PASSWORD)
print(f"Created access point {AP_SSID}")

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)


@server.route("/message1", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Melding 1 mottatt:", data)
    warning_on()
    warning_oled_text("Too much vibration,\nTake a break!")
    time.sleep(5)
    display.sleep()
    warning_off()
    return Response(request, "OK")

@server.route("/message2", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Melding 2 mottatt:", data)
    warning_on()
    warning_oled_text("Reached Daily Dose!,\nStop Vibrating!")
    time.sleep(3)
    warning_off()
    return Response(request, "OK")




#PMSA003I
reset_pin = None

i2c = busio.I2C(board.GP1, board.GP0, frequency=100000)

pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")


mic = analogio.AnalogIn(board.GP28)

warning_sent_daily = 0
warning_sent_immidiate = 0

warning_daily_cooldown = 0
warning_immidiate_cooldown = 0

pm25_cooldown = 0
pm100_cooldown = 0

pm25_warnings_sent = 0
pm100_warnings_sent = 0



server.start(str(wifi.radio.ipv4_address_ap))
while True:
    server.poll()
    time.sleep(0.1)
    if warning_sent_daily >= 1:
        warning_hourly_cooldown -= 1
        print(warning_hourly_cooldown)
    
    print(warning_daily_cooldown)
   
   
    sound_samples = []
    for sample in range (50):
        sound_samples.append(mic.value)
    min_sample = min(sound_samples)
    max_sample = max(sound_samples)
    
    
    
    peaktopeak = max_sample - min_sample
    print(peaktopeak)
    
    if warning_sent_daily < 3: 
        if peaktopeak >= 20000 and warning_hourly_cooldown == 0:
            warning_sent_daily += 1
            warning_on()
            warning_oled_text("Loud Enviroment,\nUse safety equipment")
            time.sleep(5)
            display.sleep()
            warning_off()
            print("Hourly Warnings sent: ", warning_sent_daily)
            warning_daily_cooldown = 3000 #Defined after first message is sent, 5 minutes in milliseconds
        
            
    
    
    if warning_sent_immidiate < 3:
        if peaktopeak >= 65000 and warning_immidiate_cooldown == 0:
            warning_sent_immidiate += 1
            warning_on()
            warning_oled_text("Imminent hearing loss\nUse safety equipment")
            time.sleep(5)
            display.sleep()
            print("Immidiate Warnings sent :", warning_sent_immidiate)
            warning_immidiate_cooldown = 1200 #leaves 2 minutes until next warning
       
    
    
    try:
        aqdata = pm25.read() 
        threshold_pm25 = 45 #Threshold defined through Time Weighted Average fro an 8 hour workday.
        threshold_pm10 = 135 #Threshold defined through Time Weighted Average fro an 8 hour workday.
        
        pm250 = aqdata["pm25 standard"]
        pm100 = aqdata["pm100 standard"]
        
        print(pm250)
        print(pm100)
        
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue
    if pm25_warnings_sent < 3:
        if pm250 >= threshold_pm25 and pm25_cooldown == 0:
            warning_on()
            oled_warning_text("Bad Air Quality,\n Wear a mask")
            time.sleep(5)
            display.sleep() #Dokumenter
            warning_off()
            pm25_cooldown = 3000
            pm25_warnings_sent += 1
     
    
    if pm100_warnings_sent < 3:
        if pm100 >= threshold_pm10 and pm100_cooldown == 0:
            warning_on()
            oled_warning_text("Bad Air Quality,\nWear a mask")
            time.sleep(5)
            display.sleep()
            warning_off()
            pm100_cooldown = 3000
            pm100_warnings_sent += 1
            
