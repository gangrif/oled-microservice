#!/usr/bin/python

# Winstar WEG010032ALPP5N00000 Graphic OLED and WS0010 OLED driver code for
# Raspberry Pi GPIO library. Some code originally found at
# http://forums.adafruit.com/viewtopic.php?f=8&t=29207&start=15#p163445
# Based on http://www.rpiblog.com/2012/11/interfacing-16x2-lcd-with-raspberry-pi.html
# Massive respec to UHCLEM in that post for getting me on the right track.
#
# Timing & initialisation issues resolved with help of LCD Initialization guide
# http://web.alfredstate.edu/weimandn/lcd/lcd_initialization/lcd_initialization_index.html
# I also found this helpful http://www.8051projects.net/lcd-interfacing/commands.php
#
# Find the latest version of this file at https://gist.github.com/lardconcepts/4947360/
# Fork and comment but I'd REALLY appreciate getting the graphics mode working.
# I'm trying to achieve "full height" letters, 32 pixels high. Anyone?
#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#
# For Winstar WEG1xxxxxx OLED displays, I've wired it up as follows:
#   OLED PN    | FUNCT    | GPIO    | P1 pin
#       4        RS        25        22
#       5        R/W        18        12
#       6        E        24        18
#        11        D4        23        16
#       12        D5        17        11
#       13        D6        21        13
#       14        D7        22        15
#       15        CS1        9        21
#       16        CS2        1        5
#
#   Handy Binary to Hex converter
#   0x0 = 0000    0x1 = 0001    0x2 = 0010    0x3 = 0011    0x4 = 0100    0x5 = 0101
#   0x6 = 0110    0x7 = 0111    0x8 = 1000    0x9 = 1001    0xa = 1010    0xb = 1011
#   0xc = 1100    0xd = 1101    0xe = 1110    0xf = 1111
#
#   For some reason, with the Winstar in 4-bit mode, the command needs 0x00 before
#   the real command. For example, shift whole display right is 0001,1100 = 0x01,0x0c
#   So you prefix with 0x00 and, in the next command, combine the two 4-groups into 0x1c eg:
#   lcd.write4bits(0x00)
#  lcd.write4bits(0x1c)
#
# PS - Adafruit WebIDE FTMFW! http://learn.adafruit.com/webide/


import RPi.GPIO as GPIO
from time import sleep


class Winstar_GraphicOLED:

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10s = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self):
        numlines = 2
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        #print('self init')
        

    def oledReset(self, pin_rw=14, pin_cs1=9, pin_cs2=23, pin_rs=4, pin_e=15, pins_db=[17, 18, 27, 22]):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        #GPIO.cleanup()
        pins_db1 = [4, 14, 15, 17, 18, 27, 22, 9, 23]
        for pin in pins_db1:
           GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        self.pin_rw = pin_rw
        self.pin_rs = pin_rs
        self.pin_cs1 = pin_cs1
        self.pin_cs2 = pin_cs2
        self.pin_e = pin_e
        self.pins_db = pins_db

        GPIO.setup(self.pin_rw, GPIO.OUT)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        GPIO.setup(self.pin_cs1, GPIO.OUT)
        GPIO.setup(self.pin_cs2, GPIO.OUT)

        GPIO.output(self.pin_rs, False)
        GPIO.output(self.pin_e, False)
        GPIO.output(self.pin_rw, False)
        GPIO.output(self.pin_cs1, False)
        GPIO.output(self.pin_cs2, False)

        self.busy_pin = 22

        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        # This is supposed to select which WS0010 display chip is active.
        # Strangely, CS2 seems to be the "primary" chip
        #GPIO.output(self.pin_cs1, GPIO.HIGH)
        #GPIO.output(self.pin_cs2, GPIO.LOW)
        self.delayMicroseconds(10000)
        GPIO.output(self.pin_cs1, GPIO.LOW)
        GPIO.output(self.pin_cs2, GPIO.HIGH)

        # copied from Adafruit_CharacterOLED.cpp

        # Step 1.   Power on, then delay > 100 ms
        # There are two different values (with two different references) specified on the datasheet flowchart
        # for this initial delay but neither reference is from when the power was first applied.
        # The delay required from power-up must obviously be more than 40 mS and I have arbitrarily chosen
        # to use 100 mS. Since this delay only occurs once it doesen't make sense to try to speed up program
        # execution time by skimping on this delay.

        self.delayMicroseconds(10000)

        # Step 2. Instruction 0011b (3h), then delay > 4.1 ms
        # This is a special case of the Function Set instruction where the lower four bits are irrelevant.
        # These four bits are not shown on the flowcharts because the host microcontroller does not usually
        # implement them at all (as opposed to the 8-bit mode wher they are implemented as '0's).
        # This first instruction, for some unexplained reason, takes significantly longer to complete
        # than the ones that come later.

        self.write4bits(0x03, True)
        self.delayMicroseconds(5000)
        self.write4bits(0x08, True)  # turn display off
        self.delayMicroseconds(5000)
        # Step 3.   Instruction 0011b (3h), then delay > 100 us
        # This is a second instance of the special case of the Function Set instruction.
        # The controller does not normally expect to receive more than one 'Function Set'
        # instruction so this may account for the longer than normal execution time.

        self.write4bits(0x03, True)
        self.delayMicroseconds(500)

        # Step 4.   Instruction 0011b (3h), then delay > 100 us
        # This is a third instance of the special case of the Function Set instruction.
        # By now the LCD controller realizes that what is really intended is a 'reset',
        # and it is now ready for the real Function Set instruction followed by the rest
        # of the initialization instructions.   The flowcharts do not specify what time delay belongs here.
        # I have chosen 100 us to agree with the previous instruction.   It may be possible to check the busy flag here.

        self.write4bits(0x03, True)
        self.delayMicroseconds(500)

        # Step 5.   Instruction 0010b (2h), then delay > 100 us
        # Here is where the LCD controller is expecting the 'real' Function Set instruction which,
        # in the 8-bit mode, would start with 0011. Instead, it gets a Function Set instruction starting with 0010.
        # This is it's signal to again ignore the lower four bits, switch to the four-bit mode, and expect another
        # 'real' Function Set instruction.   Once again the required time delay is speculation.
        self.write4bits(0x02, True)
        self.delayMicroseconds(500)

        # should now be in 4 bit mode with pairs of commands
        # Step 6.   Instruction 0010b (2h), then 1000b (8h), then delay > 53 us or check BF
        # This is the real Function Set instruction. This is where the interface, the number of lines, and the font are specified.

        self.write4bits(0x02)
        self.write4bits(0x0c)
        self.delayMicroseconds(500)

        # Step 7.   Instruction 0000b (0h), then 1000b (8h) then delay > 53 us or check BF
        # This is the Display on/off Control instruction.

        self.write4bits(0x0)
        self.write4bits(0x0c)
        self.delayMicroseconds(500)

        # Step 8.   Instruction 0000b (0h), then 0001b (1h) then delay > 3 ms or check BF
        # This is the Clear Display instruction

        self.write4bits(0x0)
        self.write4bits(0x01)
        self.delayMicroseconds(500)

        # Step 9. Instruction 0000b (0h), then 0110b (6h), then delay > 53 us or check BF
        # This is the Entry Mode Set instruction.

        self.write4bits(0x0)
        self.write4bits(0x06)
        self.delayMicroseconds(100)

        # Step 11.   Instruction 0000b (0h), then 1100b (0Ch), then delay > 53 us or check BF
        # This is another Display on/off Control instruction where the display is turned on and
        # where the cursor can be made visible and/or the cursor location can be made to blink.
        # This example shows the the display, curson and flashing on.
        self.write4bits(0x0)
        self.write4bits(0x00)

        self.delayMicroseconds(10000)


    def waitForReady(self):
        self.busy = True
        GPIO.setup(self.busy_pin, GPIO.IN)
        GPIO.output(self.pin_rs, False)
        GPIO.output(self.pin_rw, True)
        n = 1
        while True:
            GPIO.output(self.pin_e, False)
            GPIO.output(self.pin_e, True)

            self.delayMicroseconds(20)
            self.busy = GPIO.input(self.busy_pin)
            GPIO.output(self.pin_e, False)
            self.pulseEnable()
            n = n + 1
            if (n == 200):
                print('timeout' + str(n))
                #self.oledReset()
            if (self.busy == False) | (n == 200):
                break

        GPIO.setup(self.busy_pin, GPIO.OUT)
        GPIO.output(self.pin_rw, False)


    def home(self):

        self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
        self.delayMicroseconds(2000) # this command takes a long time!


    def clear(self):

        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        self.delayMicroseconds(2000) # 2000 microsecond sleep, clearing the display takes a long time


    def setCursor(self, col, row):

        #self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]
        self.row_offsets = [ 0x00, 0x02, 0x14, 0x54 ]

        #if (row > self.numlines):
        #    row = self.numlines - 1 # we count rows starting w/0

        #self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))
        #print "DEBUG!!", col,  self.row_offsets[row], col+self.row_offsets[row]

        self.write4bits(col + self.row_offsets[row])


    def noDisplay(self):
        ''' Turn the display off (quickly) '''

        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def display(self):
        ''' Turn the display on (quickly) '''

        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noCursor(self):
        ''' Turns the underline cursor on/off '''

        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def cursor(self):
        ''' Cursor On '''

        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def noBlink(self):
        ''' Turn on and off the blinking cursor '''

        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)


    def DisplayLeft(self):
        ''' These commands scroll the display without changing the RAM '''

        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)


    def scrollDisplayRight(self):
        ''' These commands scroll the display without changing the RAM '''

        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);


    def leftToRight(self):
        ''' This is for text that flows Left to Right '''

        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);


    def rightToLeft(self):
        ''' This is for text that flows Right to Left '''
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def autoscroll(self):
        ''' This will 'right justify' text from the cursor '''

        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def noAutoscroll(self):
        ''' This will 'left justify' text from the cursor '''

        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)


    def write4bits(self, bits, char_mode=False):
        ''' Send command to LCD '''

        self.delayMicroseconds(1000) # 1000 microsecond sleep

        bits = bin(bits)[2:].zfill(8)
        #print "%s" % bits
        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        self.pulseEnable()

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i - 4], True)

        self.pulseEnable()
        self.waitForReady()
        #self.delayMicroseconds(5)
#    def write4bits(self, bits, char_mode=False):
#        """ Send command to LCD """
#        self.delayMicroseconds(1000)  # 1000 microsecond sleep
#        bits = bin(bits)[2:].zfill(8)
#        #print "%s" % bits
##        self.GPIO.output(self.pin_rs, char_mode)
#        GPIO.output(self.pin_rs, char_mode)
#        for pin in self.pins_db:
##            self.GPIO.output(pin, False)
#            GPIO.output(pin, False)
#        for i in range(4):
#            if bits[i] == "1":
##                self.GPIO.output(self.pins_db[::-1][i], True)
#                GPIO.output(self.pins_db[::-1][i], True)
#        self.pulseEnable()
#        for pin in self.pins_db:
##            self.GPIO.output(pin, False)
#            GPIO.output(pin, False)
#        for i in range(4, 8):
#            if bits[i] == "1":
##                self.GPIO.output(self.pins_db[::-1][i-4], True)
#                GPIO.output(self.pins_db[::-1][i-4], True)
#        self.pulseEnable()
#        self.waitForReady()



    def delayMicroseconds(self, microseconds):
        seconds = microseconds / 1000000 # divide microseconds by 1 million for seconds
        sleep(seconds)


    def pulseEnable(self):
        GPIO.output(self.pin_e, False)
        self.delayMicroseconds(10) # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.pin_e, True)
        self.delayMicroseconds(10) # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.pin_e, False)
        self.delayMicroseconds(100) # commands need > 37us to settle


    def message(self, text):
        ''' Send string to LCD. Newline wraps to second line'''

        for char in text:
            if char == '\n':
                self.write4bits(0xC0) # next line
            else:

                self.write4bits(ord(char), True)
                #print "char: %s" % ord(char)


if __name__ == '__main__':

    lcd = Winstar_GraphicOLED()
    lcd.oledReset()
    #lcd.oledReset()
    lcd.home()
    lcd.clear()

    lcd.message("20 chars/line Line 2, the 2nd line")
#    lcd.message("Hello Rich")

    sleep(1)
    
    lcd.clear()
    lcd.home()
    
    GPIO.output(lcd.pin_rs, True)
    sleep(0.5)
#    for i in range(0x10, 0x42):
#        lcd.write4bits(i, True)
    lcd.clear()
    #lcd.write4bits(0x01)
    sleep(0.5)
    #lcd.pulseEnable()
    #lcd.waitForReady()
    GPIO.output(lcd.pin_rs, False)


'''    
    lcd.clear()
    lcd.home()  
    
    for i in range(0, 256):
        sleep(0.001)
        #lcd.clear()
        #sleep(0.01)
        lcd.home()
        #sleep(0.01)
        lcd.message(str(i))

    OK, let's do a little dance. Cursor: move to the left please.

    for i in range(0, 19):
        sleep(0.025)
        lcd.write4bits(0x00)
        lcd.write4bits(0x10)

    sleep(1)
    lcd.write4bits(0x8)
    sleep(1)
    
    # Turn yourself off and on again.

    for i in range(0, 3):
        sleep(0.25)
        lcd.write4bits(0x00)
        lcd.write4bits(0x08)
        sleep(0.25)
        lcd.write4bits(0x00)
        lcd.write4bits(0x0E)

    # Everyone, move 5 steps to the right

    for i in range(0, 5):
        sleep(0.025)
        lcd.write4bits(0x00)
        lcd.write4bits(0x1C)

    # And now, 5 steps back to the left again

    for i in range(0, 5):
        sleep(0.025)
        lcd.write4bits(0x00)
        lcd.write4bits(0x18)


# ... and rest!

# lcd.write4bits(0x00)
#lcd.write4bits(0x08)'''
