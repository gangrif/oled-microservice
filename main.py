#!/usr/bin/python
from oledtest import Winstar_GraphicOLED
import ledfun as oled
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask.ext.jsonpify import jsonify

# OLED init
lcd = Winstar_GraphicOLED()
lcd.oledReset()
oled.init_display()
oled.display_off()
oled.display_on(show_cursor=False)



app = Flask(__name__)
api = Api(app)


class message(Resource):
    def get(self, message, header):
        result=oledDisplay(header,message)
        return jsonify(result)


api.add_resource(message, '/message/<header>/<message>') # Route_3


def oledDisplay(header,message):
    # if msgType == 'p':
    #     header = 'Pwned!:'
    # elif msgType == 'h':
    #     header = 'Recent host:'

        # if lastDisplay:
        #     oled.chompit()
        # else:
        #     oled.clear_display()
    # oled.clear_display()
    oled.chompit()
    oled.shift_display(right=True, count=16)
    oled.set_pos(0,0)
    oled.write_string(header)
    oled.shift_display(right=False, count=16)
    oled.set_pos(1,0)
    tdelay = 0.1
    oled.write_string(message.center(16), typeomatic_delay=tdelay)
    return 1



def main():
     app.run(port='5002')




if __name__ == '__main__':
    main()
