#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: fuck@0day5.com
#
import time
import ctypes,sys
import platform

def get_current_isostr():
    iso = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()) 
    return iso

if platform.system()=='Linux' or platform.system()=='Darwin':
    class colors:
        BLACK         = '\033[0;30m'
        DARK_GRAY     = '\033[1;30m'
        LIGHT_GRAY    = '\033[0;37m'
        BLUE          = '\033[0;34m'
        LIGHT_BLUE    = '\033[1;34m'
        GREEN         = '\033[0;32m'
        LIGHT_GREEN   = '\033[1;32m'
        CYAN          = '\033[0;36m'
        LIGHT_CYAN    = '\033[1;36m'
        RED           = '\033[0;31m'
        LIGHT_RED     = '\033[1;31m'
        PURPLE        = '\033[0;35m'
        LIGHT_PURPLE  = '\033[1;35m'
        BROWN         = '\033[0;33m'
        YELLOW        = '\033[1;33m'
        WHITE         = '\033[1;37m'
        DEFAULT_COLOR = '\033[00m'
        RED_BOLD      = '\033[01;31m'
        ENDC          = '\033[0m'

    def print_error(mess):
        mess=mess.strip('\r\n')
        print colors.RED+get_current_isostr() + mess + colors.ENDC

    def print_warm(mess):
        mess=mess.strip('\r\n')
        print colors.LIGHT_PURPLE + get_current_isostr()+ mess+ colors.ENDC

    def print_debug(mess):
        mess=mess.strip('\r\n')
        print colors.GREEN + get_current_isostr()+ mess + colors.ENDC


if platform.system()=='Windows':
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLACK = 0x0
    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN = 0x02 # text color contains green.
    FOREGROUND_RED = 0x04 # text color contains red.

    FOREGROUND_INTENSITY = 0x08 # text color is intensified.
    BACKGROUND_BLUE = 0x10 # background color contains blue.
    BACKGROUND_GREEN = 0x20 # background color contains green.
    BACKGROUND_RED = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.


    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool

    def resetColor():
        set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

    def print_error(mess):
        set_cmd_text_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        sys.stdout.write("%s %s\n" % (get_current_isostr(), msg))
        resetColor()

    def print_warm(mess):
        set_cmd_text_color(FOREGROUND_YELLOW | FOREGROUND_BLUE| FOREGROUND_INTENSITY)
        sys.stdout.write("%s %s\n" % (get_current_isostr(), msg))
        resetColor()

    def print_debug(mess):
        set_cmd_text_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        sys.stdout.write("%s %s\n" % (get_current_isostr(), msg))
        resetColor()


if __name__ == '__main__':
    mess = "hello,world"
    print_error(mess)
    print_debug(mess)
    print_warm(mess)