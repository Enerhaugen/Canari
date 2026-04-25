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

buzzer = pwmio.PWMOut(board.GP18, variable_frequency=True) #Defined buzzer, using guide: https://learn.adafruit.com/using-piezo-buzzers-with-circuitpython-arduino/circuitpython
buzzer.frequency = 440

led = digitalio.DigitalInOut(board.GP21) #Defined LED using guide: https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs/digital-outputs
led.direction = digitalio.Direction.OUTPUT
OFF = 0
ON = 2**15
def warning():
    buzzer.duty_cycle = ON
    led.value = True
    time.sleep(5)
    buzzer.duty_cycle = OFF
    led.value = False
    
    
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
    warning()
    #LCD code
    time.sleep(3)
    return Response(request, "OK")

@server.route("/message2", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Melding 2 mottatt:", data)
    warning()
    #LCD code
    time.sleep(3)
    return Response(request, "OK")
    
server.start(str(wifi.radio.ipv4_address_ap))

#Defining the PMSA00I AQ Sensor, as seen in the example provided here: https://learn.adafruit.com/pmsa003i/python-circuitpython
reset_pin = None

i2c = busio.I2C(board.GP1, board.GP0, frequency=100000)

pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")

#defines microphone
mic = analogio.AnalogIn(board.GP28)

warning_sent_hour = 0
warning_sent_immidiate = 0

#warning_immidiate_cooldown = hva enn immidiate er
warning_hourly_cooldown = 0
while True:
    server.poll()
    time.sleep(0.1)
    if warning_sent_hour >= 1:
        warning_hourly_cooldown -= 1
        print(warning_hourly_cooldown)
    
    print(warning_hourly_cooldown)
    #Sound Measuring Code
    sound_samples = []
    for sample in range (50):
        sound_samples.append(mic.value)
    min_sample = min(sound_samples)
    max_sample = max(sound_samples)
    
    
    
    peaktopeak = max_sample - min_sample
    print(peaktopeak)
    
    if warning_sent_hour < 2:
        if peaktopeak >= 20000 and warning_hourly_cooldown == 0:
            warning_sent_hour += 1
            warning()
            print("Hourly Warnings sent: ", warning_sent_hour)
            warning_hourly_cooldown = 300000
        
            #lcdkode -> fare innen 1 time
    
    
    if warning_sent_immidiate < 3:
        if peaktopeak >= 25000:
            warning_sent_immidiate += 1
            warning()
            print("Immidiate Warnings sent :", warning_sent_immidiate)
            #lcdkode -> umiddelbar hørsel fare
    
    
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
    if pm250 >= threshold_pm25:
        warning()
        #LCD code
    elif pm100 >= threshold_pm10:
        warning()
        #LCD code
    

    
