# Code Documentation:

## main.py


main.py is where most of the functionality is located. It contains the warning logic, microphone code and air quality sensor code, as well as the server code.

### Initializing Server and recieving requests:

In order to initialize the server, we used the Circuitpython HTTPServer library. As The Canari is supposed to work even without WiFi, we have to create a Manual Access Point, which will all<ow the ESP32 to connect to the Raspberry Pi Pico. An example of initializing the server was found in the HTTPServer library documentation, under Manual AP(Access Point): https://docs.circuitpython.org/projects/httpserver/en/stable/starting_methods.html
It important to note that the example uses the server.serve_forever function, which halted the program before the while-loop could be initiated. This was substituted by using the server.poll() function instead inside of the while-loop to continually check for any new requests form the ESP32. To use the server.poll() function, we must also use the server.start function. An example of this was found in the HTTPServer documentation under Tasks between requests: https://docs.circuitpython.org/projects/httpserver/en/stable/examples.html


In order to handle both of the warnings from the ESP32, we created two distinct @server.route's, with two different paths, one for each message the server will recieve. The server route is specified with a path, in our case /message1 and /message 2. They also have the methods "POST". POST is defined as a http method used to send client data to the server. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/POST


This allows us to recieve the messages from the client and handle them accordingly. An example of an implementation of @server.route is provided in the API Documentation under "route". https://docs.circuitpython.org/projects/httpserver/en/latest/api.html


### Warning Functionality

The warning functionality consists of a Piezo Buzzer, an LED Diode, and and OLED Screen. 

The piezo buzzer was configured using a guide: https://learn.adafruit.com/using-piezo-buzzers-with-circuitpython-arduino/circuitpython

The buzzer functionality was then placed in the warning() function. 

The LED functionality was also defined using a guide: https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs/digital-outputs

Likewise, the LED was also placed in the warning() function.

#### OLED Forklaring her

### PMSA003I Air Quality Sensor

The Air quality sensor was configured using this guide: 
https://learn.adafruit.com/pmsa003i/python-circuitpython

The data provided by the pm25.read() function is a key value pair, where the key is a string, and value is an int. This value can therefore be compared to a defined threshold, and whenever the threshold is reached, we can activate the warning() function and display a message on the OLED screen. The guide has already read the pm25.read() data as "aqdata". We can therefore define variables as such to read specific data from the dictionary:

pm250 = aqdata["pm25 standard"]

This can then be used in comparison with our thresholds. The thresholds were calculated using the time-weighted average for an 8 hour workday. The user will recieve a warning if they are exposed more particulate matter than they can safely breathe in an 8 hour period. The safe value threshold for PM10 exposre is 135. For PM2.5, its 45. 



### MAX4466 Mic Amp

To read accurate values from the MAX4466 microphone, we took inspiration from the following guide:

https://lastminuteengineers.com/max4466-arduino-tutorial/

The guide details how we can read peak-to-peak values from the microphone to achieve accurate readings. The difference between the implementation found in the guide and our program, is that we use an array to gather 50 samples instead of any time functions.  When the array has 50 samples, we define two variables - min_sample and max_sample. min_sample is set to the lowest value found in the array, and max_samples is set to the highest. 

To find the peak-to-peak value, we subtract min_sample from max_sample. This becomes our peak-to-peak value. We can use this value to define decibels, by utilizing a sound source and a sound meter. If the peak-to-peak value exceeds 85 decibel, the user will recieve a warning, and a message on the OLED that they should equip proper safety equipment. If the peak-to-peak value exceeds 95 decibel, they will recieve a warning, informing them that they are exposed to very high noise levels an may imminently recieve hearing damage if they are not wearing safety equipment.

To avoid the warnigns becoming a nuiscance, we will only send two warnings of exposure to decibel levels over 85, and three warnings of decibel levels over 95. The warnings will have an interval of 5 minutes between them.

### Warning Cooldowns

There must be a time interval between the users warnings, in order to avoid spamming them. To achieve this, we define variables such as warning_daily_cooldown before the loop is initiated. When a warning is sent, warning_daily_cooldown will be set to 120 000. For each time the loop is iterated, we will reduce this variable with 1. As the loop runs once every 0.1 seconds, 


## code.py

code.py is used in the ESP32. It contains the connection logic to handle the connection to the Raspberry Pi Pico, as well as the vibration sensor logic.


When the warning() function is called, the LED and Piezo Buzzer will all activate for 5 seconds, before turning off. To halt the program for a period of time, we used the time library, which gives us access to time related functionality. In this case, time.sleep was utilizd, which slept the program for 5 seconds before resuming and turning off the warnings. The function is used whenever the threshold for sound or air is reached, or when the server recieves a post request from the client.



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

The vibration sensor itself returns either True or False using the digitalio.DigitalInOut - value function. If the sensor detects vibration, this value returns a True. Otherwise, it returns a False.  If the sensor returns a True value, the vibration count will start ticking upwards, incrementing with 1 per second the vibration is active. When the counts reach the threshold, a post request will be sent to the relevant server route ("/message1" for preventative measures,  "/message2" for daily threshold) and handled accordingly by the Raspberry Pi Pico. The user will then recieve a warning in the central unit with a warning to either take preventative measures, or completely stop the task which is causing them to vibrate, depending on the threshold that has been reached.

In case the post request failed, we placed it in a try-exception block to retry sending the request.

The vibration sensor itself was implemented using the circuitpython libraries board and digitalio. The board library is used with the digitalio library, and allows us to specify the pins used by the sensor. An example of implementation was found here: 

# Er dette nok referering? hør med fahad
https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/gpio














