#!/usr/bin/env python
"""tx_example, transmitter example program to use with packetradio.py
RFM69HCW packet radio module

created Jan 15, 2017 OM
last modified - Jan 17, 2017 OM"""

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
radio=PR.Radio(0,1) # radio=PR.Radio(spi_port=0,spi_cs=1) 

radio.set_temperature_offset(-3)
print(radio.temperature())

testMessage='testing, testing, 1,2,3'

while True:
    userInput=input('Press 1 to send message, 2 to quit ')

    if userInput == 1:
        radio.transmit(testMessage,addressOn=True, address=5,packetLength=64)
    elif userInput == 2:
        break
    else:
        pass


IO.output(enablePin, False)
IO.cleanup()
radio.spi.close()
