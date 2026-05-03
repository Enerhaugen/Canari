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
led = digitalio.DigitalInOut(board.GP19) #Defined LED using guide: https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs/digital-outputs
led.direction = digitalio.Direction.OUTPUT


def warning_on():
    buzzer.duty_cycle = ON
    led.value = True

def warning_off():
    buzzer.duty_cycle = OFF
    led.value = False
    

#PMSA003I


reset_pin = None
displayio.release_displays()
i2c = busio.I2C(board.GP1, board.GP0, frequency=100000)

pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")

#OLED

displayio.release_displays()

oled_reset = None

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
    splash.pop()
    warning_off()
    return Response(request, "OK")

@server.route("/message2", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Melding 2 mottatt:", data)
    warning_on()
    warning_oled_text("Daily Limit!\nStop Vibrating!")
    time.sleep(3)
    display.sleep()
    splash.pop()
    warning_off()
    return Response(request, "OK")
@server.route("/message3", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Connection Message Recieved:", data)
    warning_on()
    warning_oled_text("Connected!")
    time.sleep(3)
    splash.pop()
    display.sleep()
    warning_off()
    return Response(request, "OK")







mic = analogio.AnalogIn(board.GP27)

warning_sent_daily = 0
warning_sent_immidiate = 0

warning_hourly_cooldown = 0
warning_immidiate_cooldown = 0

pm25_cooldown = 0
pm100_cooldown = 0

pm25_warnings_sent = 0
pm100_warnings_sent = 0



server.start(str(wifi.radio.ipv4_address_ap))
while True:
    try:
        server.poll()
    except Exception as e:
        print("Server poll error:")
        print(e)
        
    time.sleep(0.1)
    
    if warning_hourly_cooldown > 0:
        warning_hourly_cooldown -= 1
        print("Warning Hourly Cooldown: ", warning_hourly_cooldown)
    
    if warning_immidiate_cooldown > 0:
        warning_immidiate_cooldown -= 1
        print("Warning immidiate Cooldown: ", warning_immidiate_cooldown)

    if pm25_cooldown > 0:
        pm25_cooldown -= 1
        print("PM-25 Warning Cooldown: ", pm25_cooldown)

    if pm100_cooldown > 0:
        pm100_cooldown -= 1
        print("PM100 Warning Cooldown: ", pm100_cooldown)
       
   
    sound_samples = []
    for sample in range (50):
        sound_samples.append(mic.value)
    min_sample = min(sound_samples)
    max_sample = max(sound_samples)
    
    
    peaktopeak = max_sample - min_sample
    print("Peak To Peak Value: ", peaktopeak)
    
    if warning_sent_daily < 3: 
        if peaktopeak >= 20000 and warning_hourly_cooldown == 0:
            warning_sent_daily += 1
            warning_on()
            warning_oled_text("Loud Enviroment,\nUse safety equipment")
            time.sleep(5)
            splash.pop()
            display.sleep()
            warning_off()
            print("Hourly Warnings sent: ", warning_sent_daily)
            warning_hourly_cooldown = 3000 #Defined after first message is sent, 5 minutes in milliseconds
        
            
    
    
    if warning_sent_immidiate < 3:
        if peaktopeak >= 65000 and warning_immidiate_cooldown == 0:
            warning_sent_immidiate += 1
            warning_on()
            warning_oled_text("Imminent hearing loss\nUse safety equipment")
            time.sleep(5)
            display.sleep()
            splash.pop()
            warning_off()
            print("Immidiate Warnings sent :", warning_sent_immidiate)
            warning_immidiate_cooldown = 1200 #leaves 2 minutes until next warning
       
    pm250 = 0
    pm100 = 0
    
    try:
        aqdata = pm25.read() 
        threshold_pm25 = 45 #Threshold defined through Time Weighted Average fro an 8 hour workday.
        threshold_pm10 = 135 #Threshold defined through Time Weighted Average fro an 8 hour workday.
        
        pm250 = aqdata["pm25 standard"]
        pm100 = aqdata["pm100 standard"]
        
        print("PM-25 Level: ", pm250)
        print("PM-100 Level: ", pm100)
        
    except RuntimeError as e:
        print("Unable to read from sensor, retrying...")
        print(e)
        pm25 = PM25_I2C(i2c, reset_pin)
        time.sleep(1)
        #continue - legg til denne igjen om det køker seg
    
    if pm25_warnings_sent < 3:
        if pm250 >= threshold_pm25 and pm25_cooldown == 0:
            warning_on()
            warning_oled_text("Bad Air Quality,\n Wear a mask")
            time.sleep(5)
            display.sleep()
            splash.pop()
            warning_off()
            pm25_cooldown = 3000
            pm25_warnings_sent += 1
     
    
    if pm100_warnings_sent < 3:
        if pm100 >= threshold_pm10 and pm100_cooldown == 0:
            warning_on()
            warning_oled_text("Bad Air Quality,\nWear a mask")
            time.sleep(5)
            display.sleep()
            splash.pop()
            warning_off()
            pm100_cooldown = 3000
            pm100_warnings_sent += 1
            
