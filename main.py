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
    def get(self, line, message):
        result=oledDisplay(int(line),message)
        return jsonify(result)

class shiftright(Resource):
    def get(self):
        result=oled.shift_display(right=True, count=16)
        return jsonify(result)

class shiftleft(Resource):
    def get(self):
        result=oled.shift_display(right=False, count=16)
        return jsonify(result)

class chompit(Resource):
    def get(self):
        result=oled.chompit()
        return jsonify(result)
        
api.add_resource(message, '/message/<line>/<message>')
api.add_resource(shiftright, '/shiftright/')
api.add_resource(shiftleft, '/shiftleft/')
api.add_resource(chompit, '/chompit/')


def oledDisplay(line,message):
    oled.set_pos(line,0)
    oled.write_string(message)
    return 1



def main():
     app.run(host='0.0.0.0', port='5002')




if __name__ == '__main__':
    main()
