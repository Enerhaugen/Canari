# Code Documentation:

## main.py


main.py is where most of the functionality is located. It contains the warning logic, microphone code and air quality sensor code, as well as the server code.

### Initializing Server and recieving requests:

In order to initialize the server, we used the Circuitpython HTTPServer library. As The Canari is supposed to work even without WiFi, we have to create a Manual Access Point, which will all<ow the ESP32 to connect to the Raspberry Pi Pico. An example of initializing the server was found in the HTTPServer library documentation, under Manual AP(Access Point): https://docs.circuitpython.org/projects/httpserver/en/stable/starting_methods.html
It important to note that the example uses the server.serve_forever function, which halted the program before the while-loop could be initiated. This was substituted by using the server.poll() function instead inside of the while-loop to continually check for any new requests form the ESP32. To use the server.poll() function, we must also use the server.start function. An example of this was found in the HTTPServer documentation under Tasks between requests: https://docs.circuitpython.org/projects/httpserver/en/stable/examples.html


In order to handle both of the warnings from the ESP32, we created two distinct @server.route's, with two different paths, one for each message the server will recieve. The server route is specified with a path, in our case /message1 and /message 2. They also have the methods "POST". POST is defined as a http method used to send client data to the server. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/POST


This allows us to recieve the messages from the client and handle them accordingly. An example of an implementation of @server.route is provided in the API Documentation under "route". https://docs.circuitpython.org/projects/httpserver/en/latest/api.html




## code.py

code.py is used in the ESP32. It contains the connection logic to handle the connection to the Raspberry Pi Pico, as well as the vibration sensor logic.

### Connecting the ESP32 to the Raspberry Pi Pico Access Point and sending post requests:


In order to connect to the access point created on the Pi Pico, the documentation specifies that we must use the wifi.radio.connect, and specify the networks SSID and its password. Found under class wifi.Radio - Connect in the documentation: 

https://docs.circuitpython.org/en/10.0.3/shared-bindings/wifi/index.html 

The connection logic was placed in a while-loop and a try-except block, to ensure that the program will continously try to connect to the access point if the initial attempt fails. When connection has been established, the while loop will break. 

To send the data to the server, we utilzed the adafruit_requests.Session class, with the post function to send a HTTP post request to the server. After the post request is sent, we use the .close() function in order to free the socket. The URL in the post requests was specified to reach the relevant server routes. Documentation was found here, under adafruit_requests.Response, and adafruit_requests.Session:

https://docs.circuitpython.org/projects/requests/en/latest/api.html#implementation-notes

An example of implementation was found here: 
https://docs.circuitpython.org/projects/requests/en/2.0.5/examples.html


### Vibration sensor logic

The vibration sensor is incapable of sensing the intensity and strength of a vibration, and can only return a boolean. We must therefore use a baseline and calculate how long the vibration sensor needs to vibrate before we must send a warning to the user. The baseline was chosen by selecting a handheld tool that exposes the user to strong vibrations. The tool selected excerted a vibration strength of 20 m/s², which we used to calculate the baseline.

We calculated this baseline to be 7,5 minutes before preventative measures must be taken, and 30 minutes before the daily threshold has been reached. Since we use time.sleep as our timing mechanism, we must calculate this threshold to seconds. We therefore end up with 450 seconds before the preventative warning is sent, and 1800 seconds before the daily threshold is reached. To account for potential false negatives and time spent sending the post request, we reduced this to 420 seconds and 1680 seconds respectively.

The vibration sensor itself returns either True or False using the digitalio.DigitalInOut - value function. If the sensor detects vibration, this value returns a True. Otherwise, it returns a False.  If the sensor returns a True value, the vibration count will start ticking upwards, incrementing with 1 per second the vibration is active. When the counts reach the threshold, a post request will be sent to the relevant server route (/message1 or /message2) and handled accordingly by the Raspberry Pi Pico. The user will then recieve a warning in the central unit with a warning to either take preventative measures, or completely stop the task which is causing them to vibrate, depending on the threshold that has been reached.

In case the post request failed, we placed it in a try-exception block to retry sending the request.

The vibration sensor itself was implemented using the circuitpython libraries board and digitalio. The board library is used with the digitalio library, and allows us to specify the pins used by the sensor. An example of implementation was found here: 

# Er dette nok referering? hør med fahad
https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/gpio














