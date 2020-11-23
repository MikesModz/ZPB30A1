#!/usr/bin/env python3
import sys
import os
import serial
import datetime
from datetime import datetime
from time import sleep

logo = """
  /$$$$$$$$ /$$$$$$$  /$$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$    /$$
 |_____ $$ | $$__  $$| $$__  $$ /$$__  $$ /$$$_  $$ /$$__  $$ /$$$$
      /$$/ | $$  \ $$| $$  \ $$|__/  \ $$| $$$$\ $$| $$  \ $$|_  $$
     /$$/  | $$$$$$$/| $$$$$$$    /$$$$$/| $$ $$ $$| $$$$$$$$  | $$
    /$$/   | $$____/ | $$__  $$  |___  $$| $$\ $$$$| $$__  $$  | $$
   /$$/    | $$      | $$  \ $$ /$$  \ $$| $$ \ $$$| $$  | $$  | $$
  /$$$$$$$$| $$      | $$$$$$$/|  $$$$$$/|  $$$$$$/| $$  | $$ /$$$$$$
 |________/|__/      |_______/  \______/  \______/ |__/  |__/|______/
"""


MODE_CC = 0
MODE_CV = 1
MODE_CP = 2
MODE_CR = 3


def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def set_mode():
    new_mode = MODE_CC
    print("")
    print(" 1) Constant current mode (CC)")
    print(" 2) Constant voltage mode (CV)")
    print(" 3) Constant power mode (CP)")
    print(" 4) Constant resistance mode (CR)")
    select = input("\nSelect operating mode [1-4]: ")
    try:
        select = int(select) - 1
    except ValueError:
        select = int(99)
    if select == 0:
        new_mode = MODE_CC
    elif select == 1:
        new_mode = MODE_CV
    elif select == 2:
        new_mode = MODE_CP
    elif select == 3:
        new_mode = MODE_CR
    else:
        new_mode = -99
    print("")
    return new_mode


def set_set_point(mode):
    set_point = 0
    if mode == MODE_CC:
        set_point = input("\nPlease set set_point current (mA) : ")
    if mode == MODE_CV:
        set_point = input("\nPlease set set_point voltage (mV) : ")
    if mode == MODE_CP:
        set_point = input("\nPlease set set_point power (mW) : ")
    if mode == MODE_CR:
        set_point = input("\nPlease set set_point resistance (divided by 0.1R) : ")
    try:
        set_point = int(set_point)
        if set_point > 65535:
            set_point = 65535
    except ValueError:
        print("Error please try again!")
    return set_point


def enable_load(mode, set_point, ser):
    if mode == MODE_CC:
        print("\nEnabling constant current mode.")
        ser.write(b'M0\r\n')
        sleep(0.5)
        print("Setting set point current to %u mA." % set_point)
        send_string = "c%u\r\n" % set_point
        ser.write(send_string.encode())
        sleep(0.5)
    elif mode == MODE_CV:
        print("\nEnabling constant voltage mode.")
        ser.write(b'M3\r\n')
        sleep(0.5)
        print("Setting set point voltage to %u mV." % set_point)
        send_string = "v%u\r\n" % set_point
        ser.write(send_string.encode())
        sleep(0.5)
    elif mode == MODE_CP:
        print("\nEnabling constant power mode.")
        ser.write(b'M1\r\n')
        print("Setting set point power to %u mW." % set_point)
        send_string = "w%u\r\n" % set_point
        ser.write(send_string.encode())
        sleep(0.5)
    elif mode == MODE_CR:
        print("\nEnabling constant resistance mode.")
        ser.write(b'M2\r\n')
        print("Setting set point resistance to %u R." % (set_point * 0.1))
        send_string = "r%u\r\n" % set_point
        ser.write(send_string.encode())
        sleep(0.5)
    print("Activating load now.")
    ser.write(b'R\r\n')
    sleep(0.5)


def disable_load(ser):
    ser.write(b'S\r\n')


def show_live_data(mode, ser):
    secs = 0
    print("Starting live update.\n")
    ser.flushInput()
    try:
        loop = True
        while loop:
            ser.write(b'D\r\n')
            b_array = ser.readline()
            if len(b_array):
                line = b_array.decode("utf-8").rstrip()
                lines = line.split(',')
                time_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                if len(lines) == 9:
                    if lines[0] == 'D':
                        status = "DISABLED"
                    elif lines[0] == 'A':
                        status = "ACTIVE"
                    else:
                        status = "OUT_OF_REG"
                    modes = ["CC", "CV", "CP", "CR"]
                    new_row = ["%2.3fC" % (int(lines[2]) * 0.1), "%2.3fV" % (int(lines[3]) / 1000.0),
                            "%2.3fV" % (int(lines[4]) / 1000.0), "%2.3fV" % (int(lines[5]) / 1000.0),
                            "%2.3fA" % (int(lines[6]) / 1000.0)]
                    print(time_date + "   ", end="")
                    for i in new_row:
                        t = "%-9s" % i
                        print(t, end="")
                    print(" " + status + " " + modes[mode])
                else:
                    print(time_date + "   No or unexpected response!")
            else:
                time_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                print(time_date + "   No response!")
            sleep(1)
    except KeyboardInterrupt:
        print("")
        return


def show_logo():
    print(logo, end="")
    print("=-=-=-=-=-==-=-=- 60W Electronic DC Load Controller -=-=-=-=-=-=-=-=-=")
    print("")


def print_menu(mode, set_point):
    modes = ["CC", "CV", "CP", "CR"]
    units = ["mA", "mV", "mW", "x 0.1R" ]
    print("Please select an option (x = Exit) :-\n")
    print(" 1) Set the operating mode (CC, CV, CP or CR) Mode = " + modes[mode])
    print(" 2) Set operating set_point value. Setpoint = %u %s" % (set_point, units[mode]))
    print(" 3) Activate load (Ctrl+C to de-activate)")


def main():
    if len(sys.argv) != 2:
        show_logo()
        print("Useage: python " + os.path.basename(__file__) + " <serial_port>\nExample: python control.py /dev/ttyUSB0\n")
        sys.exit()
    #print(len(sys.argv))
    #print(sys.argv)
    mode = MODE_CC
    set_point = 1000
    try:
        show_logo()
        ser = serial.Serial(port=sys.argv[1], baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)
        print("Opening serial port %s @ %s baud %s data bits %s parity %s stop bits.\n" % (
        ser.port, ser.baudrate, ser.bytesize, ser.parity, ser.stopbits))
        ser.isOpen()
        ser.write(b'!')
        loop = True
        while loop:
            print_menu(mode, set_point)
            select = input("\nEnter your choice [1-3]: ")
            if select == 'x':
                ser.write(b'S\r\n')
                ser.close()
                sys.exit()
            try:
                select = int(select) - 1
            except ValueError:
                select = int(99)
            if select == 0:
                new_mode = set_mode()
                if new_mode != -99:
                    if new_mode != mode:
                        set_point = 1000
                        mode = new_mode
            elif select == 1:
                set_point = set_set_point(mode)
            elif select == 2:
                enable_load(mode, set_point, ser)
                show_live_data(mode, ser)
                disable_load(ser)
            else:
                print("")
    except KeyboardInterrupt:
        ser.write(b'S\r\n')
        ser.close()
        return
    except Exception as e:
        print("Program failed ({})", e)
        ser.write(b'S\r\n')
        ser.close()
        return
    else:
        return


if __name__ == "__main__":
    main()
