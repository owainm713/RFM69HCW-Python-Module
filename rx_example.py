#!/usr/bin/env python
"""rx_example, receiver example program to use with packetradio.py
RFM69HCW packet radio module

created Jan 15, 2017 OM
last modified - Jan 16, 2017 OM"""

"""
Copyright 2017 Owain Martin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import RPi.GPIO as IO
import packetradio as PR
import time, sys

enablePin = 26
resetPin = 19

# set up GPIO settings
IO.setwarnings(False)
IO.setmode(IO.BCM)

IO.setup(enablePin, IO.OUT)
IO.output(enablePin, False)
IO.setup(resetPin, IO.OUT)
IO.output(resetPin, False)

# radio setup

IO.output(enablePin, True)    
radio=PR.Radio(0,1)

radio.set_temperature_offset(-3)
print(radio.temperature())

def print_radio_data():
    """print_radio_data"""
    
    while len(radio.receiveData) > 0:
        data=radio.receiveData.pop(0)                
        print(data)            

    return

while True:
    mode=input('Pick receive mode 1 - Foreground, 2 - Background, Press 3 to Quit ')

    if mode == 3:
        break

    if mode != 1 and mode !=2:
        continue

    timer=input('Set time for receiver to be on (s) ')

    if mode == 1:
        radio.receiveData=[]  # clear receiveData list                
        radio.receive(timer)  # dataList = radio.receive(timer) is also valid
        for line in radio.receiveData:
            print(line)

    else: # mode = 2
        radio.receiveData=[]  # clear receiveData list                
        radio.receive(timer, True)
        for i in range(0,25):            
            print_radio_data()            
            time.sleep(0.5)


IO.output(enablePin, False)
IO.cleanup()
radio.spi.close()
        

        
