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

class cls-chompit(Resource):
    def get(self):
        result=oled.chompit()
        return jsonify(result)

class cls(Resource):
    def get(self):
        result=oled.clear_display()
        return jsonify(result)

class credits(Resource):
    def get(self):
        result=oled.lib_credits()
        return jsonify(result)

class demo(Resource):
    def get(self):
        result=oled.demo()
        return jsonify(result)

api.add_resource(shiftright, '/credits')
api.add_resource(shiftright, '/demo')
api.add_resource(message, '/message/<line>/<message>')
api.add_resource(shiftright, '/shiftright')
api.add_resource(shiftleft, '/shiftleft')
api.add_resource(chompit, '/cls-chompit')
api.add_resource(chompit, '/cls')


def oledDisplay(line,message):
    oled.set_pos(line,0)
    oled.write_string(message)
    return 1



def main():
     app.run(host='0.0.0.0', port='5002') # Runs on all interfaces, Change host= to the IP you'd like to bind to if needed
#     app.run(port='5002') # Runs on localhost



if __name__ == '__main__':
    main()
