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

The LED functionality was also defined using a guide: https://learn.adafruit.com/circuitpython-digital-inputs-and-outputs/digital-outputs

Both the Buzzer and the LED functionality was placed inside of the warning_on() and warning_off() functionality, that is called whenever a threshold is crossed.







### PMSA003I Air Quality Sensor

The Air quality sensor was configured using this guide: 
https://learn.adafruit.com/pmsa003i/python-circuitpython

The data provided by the pm25.read() function is a key value pair, where the key is a string, and value is an int. This value can therefore be compared to a defined threshold, and whenever the threshold is reached, we can activate the warning functions and display a message on the OLED screen. The guide has already read the pm25.read() data as "aqdata". We can therefore define variables to read specific data from the dictionary:

pm250 = aqdata["pm25 standard"]

This can then be used in comparison with our thresholds. The thresholds were calculated using the time-weighted average for an 8 hour workday. The user will recieve a warning if they are exposed more particulate matter than they can safely breathe in an 8 hour period. The safe value threshold for PM10 exposre is 135. For PM2.5, its 45. 


#### OLED Screen

The OLED will display usefull information and provide context to the warnings. An implementation of the OLED screen was found here: https://docs.circuitpython.org/projects/displayio_ssd1306/en/latest/examples.html

To tailor the code to our purpose, we removed the bitmap and set the height to HEIGH // 5, to fit two rows of text on the screen. The functionality that activates the screen and displays text was placed inside of the warning_oled_text(message) function, in order to reduce redundant code as it will be used frequently. Oled_reset was set to none, and the busio and board libraries was used to set I2C to the correct pins. This solution was inspired by the setup-code from the PMSA003I, where busio was used in a similiar manner to use the correct pins. An example of such an implementation of busio was found here under Circuitpython and python usage: https://learn.adafruit.com/pmsa003i/python-circuitpython

The display.sleep() and display.wake() functions are used to sleep the OLED screen when no warnings are active, and wake the screen when a warning has been sent. Both functions were found here: https://docs.circuitpython.org/projects/displayio_ssd1306/en/latest/api.html


Its important to note that both the PMSA003I and the OLED screen share the same pins - GP0 and GP1. When we tried to use different pins for the components, we recieved an error - ValueError: I2C peripheral in use

A potential solution was found on raspberrypi's forum: https://forums.raspberrypi.com/viewtopic.php?t=328834#p1968307

By connecting both components to the same pins and ensuring that they have different I2C adresses and initializing the i2c bus once, the issue was solved. We kept the example I2C adress provided by the OLED coding example (0x3). The PMSA003I already has a predefined adress (0x12), as seen here under Usage: https://learn.adafruit.com/pmsa003i/wippersnapper-setup


### MAX4466 Mic Amp

To read accurate values from the MAX4466 microphone, we took inspiration from the following guide:

https://lastminuteengineers.com/max4466-arduino-tutorial/

The guide details how we can read peak-to-peak values from the microphone to achieve accurate readings. The difference between the implementation found in the guide and our program, is that we use an array to gather 50 samples instead of any time functions.  When the array has 50 samples, we define two variables - min_sample and max_sample. min_sample is set to the lowest value found in the array, and max_samples is set to the highest. 

To find the peak-to-peak value, we subtract min_sample from max_sample. This becomes our peak-to-peak value. We can use this value to define decibels, by utilizing a sound source and a sound meter. By utilizing this technique, we found that a peak-to-peak value of roughly 20 000 corresponds to about 85 decibels, which can damage hearing over an 8 hour workday. A peak to peak value of roughly 65 000 corresponds to about 95 decibels. If the peak-to-peak value exceeds either of these values, the warning functions will be called, and the user will recieve relevant information on the OLED display.


### Warnings and Warning Cooldowns
When a threshold is crossed, a warning will be sent to the user. To avoid annoying the user, they will only recieve a limited amount of warnings. The user will therefore only recieve a warning if they have recieved fewer warnings then three. If they have recieved three warnings, we must assume that they have taken preemptive measures to avoid injury. This was done by defining a variable as 0 for each specific warning, and increasing it by 1 every time the relevant warning has been sent. If the user has recieved over 3 warnings, the warning functionality will not be called, nor the cooldowns reset.


There must be a time interval between the users warnings, in order to avoid spamming them. To achieve this, we define variables such as warning_daily_cooldown before the loop is initiated. When a warning is sent, warning_daily_cooldown will be set to 3000. As the variable will be subracted by 1 every iteration of the loop, and the loop runs once every 0.1 second, this will result in a cooldown of 5 minutes before a warning can be sent again. In cases where the health of the user is in immidiate danger, such as when they are exposed to over 95 decibels, the cooldown is slightly shorter, at 2 minutes.

We used the Circuitpython Time library in order to run the loop once every 0.1 seconds using the time.sleep() function. This function sleeps the program for a set amount of time by defining time.sleep as 0.1 as such:

time.sleep(0.1)

This allows us to set timers and halt the program whenever needed, such as after every time warning_on() is called. This functionality was found in the time library documentation:

https://docs.circuitpython.org/en/latest/shared-bindings/time/



## code.py

code.py is used in the ESP32. It contains the connection logic to handle the connection to the Raspberry Pi Pico, as well as the vibration sensor logic.


When the warning() function is called, the LED and Piezo Buzzer will all activate for 5 seconds, before turning off. To halt the program for a period of time, we used the time library, which gives us access to time related functionality. In this case, time.sleep was utilized, which slept the program for 5 seconds before resuming and turning off the warnings. The function is used whenever the threshold for sound or air is reached, or when the server recieves a post request from the client.





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


https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/gpio

# Er dette nok referering? hør med fahad












