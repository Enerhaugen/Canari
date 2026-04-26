Code Documentation:

Initializing Server:

In order to initialize the server, we used the Circuitpython HTTPServer library. As The Canari is supposed to work even without WiFi, we have to create a Manual Access Point, which will all<ow the ESP32 to connect to the Raspberry Pi Pico. An example of initializing the server was found in the HTTPServer library documentation, under Manual AP(Access Point): https://docs.circuitpython.org/projects/httpserver/en/stable/starting_methods.html
It important to note that the example uses the server.serve_forever function, which halted the program before the while-loop could be initiated. This was substituted by using the server.poll() function instead inside of the while-loop to continually check for any new requests form the ESP32. To use the server.poll() function, we must also use the server.start function. An example of this was found in the HTTPServer documentation under Tasks between requests: https://docs.circuitpython.org/projects/httpserver/en/stable/examples.html


In order to handle both of the warnings from the ESP32, we created two distinct @server.route's, with two different paths, one for each message the server will recieve. The server route is specified with a path, in our case /message1 and /message 2. They also have the methods "POST". POST is defined as a http method used to send client data to the server. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/POST


This allows us to recieve the messages from the client and handle them accordingly. An example of an implementation of @server.route is provided in the API Documentation under "route". https://docs.circuitpython.org/projects/httpserver/en/latest/api.html


Connecting the ESP32 to the Raspberry Pi Pico Access Point:




