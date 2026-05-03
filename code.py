import socketpool
import wifi
import time
import adafruit_requests
from adafruit_httpserver import Request, Response, Server, POST
import board
import digitalio


#Deffining the Raspberry Pi Pico's SSID and Password
WIFI_SSID = "..."
WIFI_PASSWORD = "12345678"

print(f"Connecting to {WIFI_SSID}...")
condition_connection = True
condition_message = True

vibration_sensor = digitalio.DigitalInOut(board.D0)
vibration_sensor.direction = digitalio.Direction.INPUT
message_measures = "Too much vibration, Warning!"
message_daily = "Daily Threshold Reached, Stop to prevent injury!"
message_connection = "Connected to the Pico"



vibration_count_measures = 0
vibration_count_measures_threshold = 5#420 #7 minutes

vibration_count_daily = 0
vibration_count_daily_threshold = 1680 #28 minutes
vibration_condition = True
sent_measures = False

while condition_connection:
    try: #Try-Except block to handle potential exceptions during the connection phase, if connection fails, it retries.
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected to {WIFI_SSID}")
        response = requests.post("http://192.168.4.1:5000/message3", data=message_connection)
        print("Measures Message Sent!")
        response.close()
        condition_connection = False
    except Exception as e:
        print("Feil ved tilkobling, prøver på nytt...")
        time.sleep(1)
            
    print("Connected, loop broken") #Confirms loop is broken for readability
    
while True:
    while vibration_condition == True:
        if vibration_sensor.value == True:
            vibration_count_measures += 1
            vibration_count_daily += 1
            print("Count Measures: ", vibration_count_measures)
            print("Count Daily: ", vibration_count_daily)
            time.sleep(1) #Time sleep acts as our timer. Each second, the loop will repeat and add 1 to the vibration counts, until the thresholds are reached.
        if vibration_count_measures >= vibration_count_measures_threshold: #Breaks the while loop when the threshold is crossed.
            break
        if vibration_count_daily >= vibration_count_daily_threshold: #Breaks the while loop when the threshold is crossed.
            break
        
            
    #Sends a message to the server when the threshold is crossed.
    #User wearing the Raspberry Pi Pico will recieve a warning that they should take preventative measures.
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
    
    #Sends a message to the server when the threshold is crossed.
    #User wearing the Raspberry Pi Pico will recieve a warning that they should stop using vibrating tools. 
    if vibration_count_daily >= vibration_count_daily_threshold:
        try:
            response = requests.post("http://192.168.4.1:5000/message2", data=message_daily)
            print("Daily Message Sent!")
            response.close()
            vibration_count_daily = 1560 #Sets the timer to 26 minutes to warn the user again if they continue to vibrate, in case the first warning was missed.
            print("done")
            
            
        except Exception as e:
            print("Couldnt send message, retrying...")
            time.sleep(1)
        
        
