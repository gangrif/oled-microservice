# Overview
This is a python API designed to interact with the OLED library which is found here: https://github.com/gangrif/HackMyDerby2015/tree/master/scripts/oled

A copy of this library is included here.

This is a work in progress.  Executing main.py starts an api on 0.0.0.0:5002.  You can call it via curl, and display things on your OLED display. You can switch to localhost by editing main.py if you'd like to protect the api.

This assumes you have a Raspberry Pi working, with a winstar 16x2 character OLED.

# Running the app
## Direct on Pi
If you intend to run this on the host raspbarry pi, you'll need to install a few OS packages, and some Python packages:
  apt-get install python-pip g++ python-dev
  pip install RPi.GPIO flask flask-jsonpify flask-restful

## Via Docker
If you intent to run the service in docker, you'll just need to get Docker setup, and then the python/OS packaged get applied to the docker conteriner.
I am running docker on raspbian Jessie, using the following directions:
https://github.com/umiddelb/armhf/wiki/Get-Docker-up-and-running-on-the-RaspberryPi-(ARMv6)-in-four-steps-(Wheezy)

The container itself needs to be built, and then run with the --privileged flag.  This is because your container can't access GPIO without root.  Maybe this can be worked around.

To build the container:
  Inside of the root of this repo, simply docker build -t oled-microservice .

Then run the container as you would, adding the --privileged flag.
  sudo docker run -p 127.0.0.1:5002:5002 --privileged oled-microservice
That will run the microservice in the foreground.  It will start up on port 5002, and you can interact with it via curl, or other means.  

# endpoints
Here is a list of endpoints
  * /credits - Display the oled library credits.  (Thanks Carl!)
  * /demo - Display a short demo that's built into the OLED library
  * /cls - This clears the screen
  * /cls_chompit - This clears the screen with a pac-man animation
  * /shiftright - Shift the contents of the screen 16 characters right, including off the edge of the screen
  * /shiftleft -Shift the contents of the screen 16 characters left, including off the edge of the screen
  * /message/{line}/{message} - Write a message to line 0 or 1 of the screen ex. /message/0/Hi%20There will print "Hi There" to line 0 of the screen.
