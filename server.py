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
    
    #warning here
    time.sleep(3)
    return Response(request, "OK")

@server.route("/message2", POST)
def receive_message(request: Request):
    data = request.body.decode("utf-8")
    print("Melding 2 mottatt:", data)
    #warning here
    time.sleep(3)
    return Response(request, "OK")
server.serve_forever(str(wifi.radio.ipv4_address_ap))
