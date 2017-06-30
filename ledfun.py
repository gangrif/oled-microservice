#!/usr/bin/env python

from __future__ import print_function
import RPi.GPIO as GPIO
import sys
from time import sleep

# Symbolic constants for the OLED pins.
OLED_RS  = 4
OLED_RW  = 5
OLED_E   = 6  #this was set wrong at 18
OLED_DB4 = 11
OLED_DB5 = 12
OLED_DB6 = 13
OLED_DB7 = 14

# Symbolic constants for the GPIO pins.
GPIO_RS = 4 
GPIO_RW = 14
GPIO_E = 15
GPIO_DB4 = 17
GPIO_DB5 = 18
GPIO_DB6 = 27
GPIO_DB7 = 22
GPIO_CS2  = 23

BUSY_POLL_INTERVAL = 500

# This mapping represents how the GPIO pins are wired to the OLED pins.
OLED2GPIO_MAP = {
    OLED_RS:  GPIO_RS,
    OLED_RW:  GPIO_RW,
    OLED_E:   GPIO_E,
    OLED_DB4: GPIO_DB4,
    OLED_DB5: GPIO_DB5,
    OLED_DB6: GPIO_DB6,
    OLED_DB7: GPIO_DB7
}

def sleep_micros(microseconds):
    seconds = float(microseconds) / float(1000000) # divide microseconds by 1 million for seconds
    sleep(seconds)

def pulse():
    """
    Generates a 10 microsend width pulse used to tell the OLED to process the
    instruction loaded on the input pins.
    """
    pin_e = OLED2GPIO_MAP[OLED_E]
    GPIO.output(pin_e, False)
    sleep_micros(10)
    GPIO.output(pin_e, True)
    sleep_micros(10)
    GPIO.output(pin_e, False)
    sleep_micros(100)

def wait_not_busy():
    busy = True
    busy_pin = OLED2GPIO_MAP[OLED_DB7]
    rs_pin = OLED2GPIO_MAP[OLED_RS]
    rw_pin = OLED2GPIO_MAP[OLED_RW]
    e_pin = OLED2GPIO_MAP[OLED_E]
    GPIO.setup(busy_pin, GPIO.IN)
    GPIO.output(rs_pin, False)
    GPIO.output(rw_pin, True)
    n = 1
    while True:
        GPIO.output(e_pin, False)
        GPIO.output(e_pin, True)
        sleep_micros(20)
        busy = GPIO.input(busy_pin)
        GPIO.output(e_pin, False)
        pulse()
        n = n + 1
        if (n == 200):
            #init_display()
            #display_off()
            print('timeout => {0}'.format(n), file=sys.stderr)
        if (not busy) or (n == 200):
            break
    GPIO.setup(busy_pin, GPIO.OUT)

def send_instruction(rs=0, rw=0, db7=0, db6=0, db5=0, db4=0):
    GPIO.output(OLED2GPIO_MAP[OLED_RS], bool(rs))
    GPIO.output(OLED2GPIO_MAP[OLED_RW], bool(rw))
    GPIO.output(OLED2GPIO_MAP[OLED_DB7], bool(db7))
    GPIO.output(OLED2GPIO_MAP[OLED_DB6], bool(db6))
    GPIO.output(OLED2GPIO_MAP[OLED_DB5], bool(db5))
    GPIO.output(OLED2GPIO_MAP[OLED_DB4], bool(db4))
    pulse()

def write_string(s, typeomatic_delay=0):
    for c in s:
        write_char(c)
        if typeomatic_delay > 0:
            sleep(typeomatic_delay)

def write_char(c):
    write_raw_data(ord(c))

def write_raw_data(o):
    low = o & 0x0f
    high = o>>4
    wait_not_busy()
    for nibble in (high, low):
        db7 = bool(nibble & 0b1000)
        db6 = bool(nibble & 0b0100)
        db5 = bool(nibble & 0b0010)
        db4 = bool(nibble & 0b0001)
        send_instruction(rs=1, rw=0, db7=db7, db6=db6, db5=db5, db4=db4)

def write_cgram(d4=0, d3=0, d2=0, d1=0, d0=0):
    o = d4<<4 | d3<<3 | d2<<2 | d1<<1 | d0
    write_raw_data(o)

def set_pos(row, col):
    assert row >=0 and row <= 1, "`row` must be between 0 and 1."
    assert col >=0 and col <= 15, "`col` must be between 0 and 15."
    row_start = [0x00, 0x40]
    start = row_start[row]
    addr = start + col
    wait_not_busy()
    high = (addr>>4) | 0b1000
    low = addr & 0x0f 
    for nibble in [high, low]: 
        db7 = bool(nibble & 0b1000)
        db6 = bool(nibble & 0b0100)
        db5 = bool(nibble & 0b0010)
        db4 = bool(nibble & 0b0001)
        send_instruction(db7=db7, db6=db6, db5=db5, db4=db4)

def init_gpio_pins():
    for pin in [GPIO_RS, GPIO_RW, GPIO_E, GPIO_DB4, GPIO_DB5, GPIO_DB6, GPIO_DB7, GPIO_CS2]:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)  #added initial=gpio.low

def display_off():
    wait_not_busy()
    send_instruction()
    send_instruction(db7=1)

def display_on(show_cursor=True, blink_cursor=True):
    wait_not_busy()
    send_instruction()
    send_instruction(db7=1, db6=1, db5=show_cursor, db4=blink_cursor)

def clear_display():
    wait_not_busy()
    send_instruction()
    send_instruction(db4=1)

def return_home():
    wait_not_busy()
    send_instruction()
    send_instruction(db5=1)

def set_ddram_address(a6=0, a5=0, a4=0, a3=0, a2=0, a1=0, a0=0):
    wait_not_busy()
    send_instruction(db7=1, db6=a6, db5=a5, db4=a4)
    send_instruction(db7=a3, db6=a2, db5=a1, db4=a0)

def set_entry_mode(increment=True, shift_display=False):
    wait_not_busy()
    send_instruction()
    send_instruction(db6=1, db5=increment, db4=shift_display)

def shift_display(right=True, count=1, shift_delay=0):
    for n in range(count):
        wait_not_busy()
        send_instruction(db4=1)
        send_instruction(db7=1, db6=right)
        if shift_delay > 0:
            sleep(shift_delay)

def shift_cursor(right=True):
    wait_not_busy()
    send_instruction(db4=1)
    send_instruction(db7=0, db6=right)

def blink_line(row, col, s, on_time=0.5, off_time=0.1, count=5):
    slen = len(s)
    blank = " " * slen
    for n in range(count):
        set_pos(row, col) 
        write_string(blank)
        sleep(off_time)
        set_pos(row, col) 
        write_string(s)
        sleep(on_time)

def set_cgram_addr(a5=0, a4=0, a3=0, a2=0, a1=0, a0=0):
    wait_not_busy()
    send_instruction(db7=0, db6=1, db5=a5, db4=a4)
    send_instruction(db7=a3, db6=a2, db5=a1, db4=a0)

def init_chomp_chars():
    # Set CGRAM address
    set_cgram_addr()
    # chomp open
    write_cgram(0,0,1,0,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,1,1,1,1)
    write_cgram(1,1,1,1,0)
    write_cgram(1,1,1,0,0)
    write_cgram(1,1,1,1,0)
    write_cgram(0,1,1,1,1)
    write_cgram(0,0,1,0,0)

    # chomp closed
    write_cgram(0,0,1,0,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,1,1,1,0)
    write_cgram(1,1,1,1,1)
    write_cgram(1,1,1,1,1)
    write_cgram(0,1,1,1,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,0,1,0,0)

    # template 
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)
    #write_cgram(0,0,0,0,0)

    # hand1
    write_cgram(0,1,0,1,0)
    write_cgram(0,1,0,1,0)
    write_cgram(0,1,0,1,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,0,1,1,0)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)

    # hand2
    write_cgram(0,1,0,0,0)
    write_cgram(0,1,0,0,0)
    write_cgram(0,1,0,0,0)
    write_cgram(0,1,1,1,0)
    write_cgram(0,1,1,0,0)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)

    # light1 
    write_cgram(1,0,1,0,1)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)
    write_cgram(1,1,1,1,1)
    write_cgram(1,1,1,1,1)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)
    write_cgram(1,0,1,0,1)

    # light2
    write_cgram(1,0,0,0,1)
    write_cgram(1,1,0,1,1)
    write_cgram(0,1,0,1,0)
    write_cgram(0,0,1,0,0)
    write_cgram(0,0,1,0,0)
    write_cgram(0,1,0,1,0)
    write_cgram(1,1,0,1,1)
    write_cgram(1,0,0,0,1)

    # fader
    write_cgram(0,1,0,0,1)
    write_cgram(1,0,0,1,1)
    write_cgram(0,1,0,1,1)
    write_cgram(0,0,1,1,1)
    write_cgram(0,0,1,1,1)
    write_cgram(0,1,1,1,0)
    write_cgram(1,1,1,1,0)
    write_cgram(1,1,1,1,0)

def chompit():
    # Animation
    animate_delay = 0.05
    for row in [0, 1]:
        for col in range(16):
            set_pos(row, col)
            write_raw_data(0)
            sleep(animate_delay)
            set_pos(row, col)
            write_raw_data(1)
            sleep(animate_delay)
            set_pos(row, col)
            write_char(" ")

def wipeit():
    # Animation
    animate_delay = 0.05
    for col in range(16):
        for row in [0, 1]:
            set_pos(row, col)
            write_raw_data(6)
            sleep(animate_delay)
            set_pos(row, col)
            write_raw_data(6)
            sleep(animate_delay)
            col2 = col - 1
            set_pos(row, col)
            write_char(" ")

def wipe_row(row):
    animate_delay = 0.05
    for col in range(16):
        set_pos(row, col)
        write_raw_data(0)
        sleep(animate_delay)
        set_pos(row, col)
        write_raw_data(1)
        sleep(animate_delay)
        col2 = col - 1
        set_pos(row, col)
        write_char(" ")


def init_4bit(ft1=0, ft0=0):
    """
    ft1  ft0  font table
    ---  ---  -------------------
    0    0    English/Japanese
    0    1    Western European #1
    1    0    English/Russian
    1    1    Western European #2
    """
    wait_not_busy()
    send_instruction(db5=1)
    send_instruction(db7=1, db5=ft1, db4=ft0)

def init_display(noClear=0):
    # Initialize GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_gpio_pins()
    # Initialize OLED
    init_4bit()
    set_entry_mode()
    init_chomp_chars()
    # Turn on display, clear screen and data.
    display_on(show_cursor=False, blink_cursor=False)
    if noClear == 0:
        clear_display()

    return_home()
    set_ddram_address()

def demo():
    # Shift display right, output some text, and scroll it back into view.
    shift_display(right=True, count=16)
    set_pos(0, 0)
    write_string("Hello, OLED".center(16))
    set_pos(1, 0)
    write_string("World!".center(16))
    shift_display(right=False, count=15)
    sleep(2)
    # Run through a self-destruct sequence.
    delay = 0.05
    clear_display()
    return_home()
    set_pos(0, 0)
    write_string("Self-destruct".center(16), typeomatic_delay=delay)
    set_pos(1, 0)
    write_string("Activated!".center(16), typeomatic_delay=delay)
    blink_line(1, 0, "Activated!".center(16), on_time=0.2, off_time=0.1, count=3)
    for n in range(10, 0, -1):
        set_pos(1, 0)
        write_string("{0} ...".format(n).center(16))
        sleep(0.5)
    set_pos(1, 0)
    write_string("*BOOM!*".center(16))
    sleep(3)
    # Show credits.
    lib_credits()
    # Fancy animation to clear credits.
    chompit()
    # Game Over
    clear_display()
    blink_line(0, 0, "GAME OVER".center(16), on_time=0.5, off_time=0.1, count=5)
    set_pos(1, 0)
    write_string("Insert Coin".center(16))
    sleep(3)

def lib_credits():
    # Show credits.
    delay = 0.05
    clear_display()
    set_pos(0, 0)
    write_string("OLED library by:", typeomatic_delay=delay)
    set_pos(1, 0)
    write_string("Carl Waldbieser", typeomatic_delay=delay)
    sleep(3)


def main():
    init_display()
    demo()
    # Turn off display.
    display_off()

if __name__ == "__main__":
    main()

