import socketpool
import wifi
import time
import adafruit_requests
from adafruit_httpserver import Request, Response, Server, POST
import board
import digitalio



WIFI_SSID = "..."
WIFI_PASSWORD = "12345678"

print(f"Connecting to {WIFI_SSID}...")
condition_connection = True
condition_message = True

vibration_sensor = digitalio.DigitalInOut(board.D0)
vibration_sensor.direction = digitalio.Direction.INPUT
message_measures = "Too much vibration, Warning!"
message_daily = "Daily Threshold Reached, Stop to prevent injury!"

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context=None)

vibration_count_measures = 0
vibration_count_measures_threshold = 420 

vibration_count_daily = 0
vibration_count_daily_threshold = 1680 
vibration_condition = True
sent_measures = False

while condition_connection:
    try: 
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected to {WIFI_SSID}")
        condition_connection = False
    except Exception as e:
        print("Feil ved tilkobling, prøver på nytt...")
        time.sleep(1)
            
    print("Connected, loop broken") 
    
while True:

    while vibration_condition == True:
        if vibration_sensor.value == True:
            vibration_count_measures += 1
            vibration_count_daily += 1
            print("Count Measures: ", vibration_count_measures)
            print("Count Daily: ", vibration_count_daily)
            time.sleep(1) 
        if vibration_count_measures >= vibration_count_measures_threshold: .
            break
        if vibration_count_daily >= vibration_count_daily_threshold: 
            break
        
            
        
 

    if vibration_count_measures >= vibration_count_measures_threshold and not sent_measures: 
        try:
            response = requests.post("http://192.168.4.1:5000/message1", data=message_measures)
            print("Measures Message Sent!")
            response.close()
            sent_measures = True
            print("done")
            
            
            
        except Exception as e:
            print("Couldnt send message, retrying...")
            time.sleep(1)
    
    if vibration_count_daily >= vibration_count_daily_threshold:
        try:
            response = requests.post("http://192.168.4.1:5000/message2", data=message_daily)
            print("Daily Message Sent!")
            response.close()
            vibration_count_daily = 1560 
            print("done")
            
            
        except Exception as e:
            print("Couldnt send message, retrying...")
            time.sleep(1)
        
