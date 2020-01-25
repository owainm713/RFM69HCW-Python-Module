#!/usr/bin/env python3
"""txrx_example2, receiver example program to use with packetradio.py
RFM69HCW packet radio module

created May 4, 2017 OM
modified - May 9, 2017 OM
modified - Jan 18, 2020 OM"""

"""
Copyright 2017, 2018, 2019, 2020 Owain Martin

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
import time, sys, threading


site = 'A'
#site = 'B'

if site == 'A':
    enablePin = 26  #4, 26
    resetPin = 19   #6, 19
    intPin = 13     #5, 13
    
else:
    enablePin = 4  #4, 26
    resetPin = 6   #6, 19
    intPin = 5     #5, 13



# set up GPIO settings
IO.setwarnings(False)
IO.setmode(IO.BCM)

IO.setup(enablePin, IO.OUT)
IO.output(enablePin, False)
IO.setup(resetPin, IO.OUT)
IO.output(resetPin, False)
IO.setup(intPin, IO.IN)

# radio setup

IO.output(enablePin, True)    
radio=PR.Radio(0,1)                                 # radio=PR.Radio(spi_port=0,spi_cs=1)
radio.set_dio(dio0=1)                               # set up radio h/w interrupt out on  DIO 0
radio.set_frequency(915000000)                      # set up radio frequency
radio.set_acks(receiveAck=12,sendAck=13)            # set radio acknowledgement bytes
radio.set_sync_word(syncValueList=[0xE2,0x4A,0x26]) # set radio sync word 
radio.set_power('Pa1', 0)                           # set power
keyList = [12, 35, 245, 117, 95, 178, 233, 18, 200, 76, 117, 95, 178, 233, 97, 11]
radio.set_encryption('on', keyList)                 # set encryption

if site == 'A':
    radio.set_node_address(9)
    radio.set_interrupt_pin(13)
    toAddr = 5    
    
else:
    toAddr = 9
    radio.set_interrupt_pin(5)

radio.set_temperature_offset(-3)
print(radio.temperature())

def print_radio_data():
    """print_radio_data"""    

    while checkForInput==True:    
        while len(radio.receiveData) > 0:
            data=radio.receiveData.pop(0)

            if radio.packetFormat == 'fixed':
                if int(data[2]) == radio.receiveAck:
                    print(str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+
                          str(data[3:].decode()))
                else:
                    print(str(data[0])+' '+str(data[1])+' '+str(data[2:].decode()))

            else:   # packetFormat = 'variable'
                if int(data[3]) == radio.receiveAck:
                    print(str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+
                          str(data[3])+' '+str(data[4:].decode()))
                else:
                    print(str(data[0])+' '+str(data[1])+' '+str(data[2])+' '+
                          str(data[3:].decode()))      
           
        time.sleep(0.01)

    return    

checkForInput = True
printLoop = threading.Thread(name='print_radio_data', target=print_radio_data)
printLoop.start()

txData=['T5','Hello there', 'S1232325', 'ACK Stinky Sockes', 'ACK I love coke']

while True:
    print("Press 1 - Rx SW Int, 2 - Rx HW Int 3 - Interrupt Rx, 4 - Tx HW Int Ack, 5 - Tx SW Int Ack ")
    mode=int(input("6 - Tx No Ack, 7 - change packet format, variable/fixed, Press 8 to Quit "))

    if mode == 8:
        checkForInput = False
        break          

    if mode == 1:
        radio.receive_timeout(input('Set time for receiver to be on (s) '))
        receiveLoop = threading.Thread(name='radio.receive_sw_int', target=radio.receive_sw_int)
        receiveLoop.start()

    elif mode == 2:
        radio.receive_timeout(input('Set time for receiver to be on (s) '))
        receiveLoop = threading.Thread(name='radio.receive_hw_int', target=radio.receive_hw_int)
        receiveLoop.start()

    elif mode == 3:
        radio.receive_timeout(0)

    elif mode == 4:
        radio.receive_timeout(0)
        success, failed = radio.transmit_with_ack(txData,toAddr,intType='hw', retry=4)
        print(success, failed)
        radio.receive_timeout(60)
        receiveLoop = threading.Thread(name='radio.receive_hw_int', target=radio.receive_hw_int)
        receiveLoop.start()

    elif mode == 5:
        radio.receive_timeout(0)
        success, failed = radio.transmit_with_ack(txData,toAddr,intType='sw', retry=4)
        print(success, failed)
        radio.receive_timeout(60)
        receiveLoop = threading.Thread(name='radio.receive_sw_int', target=radio.receive_sw_int)
        receiveLoop.start()

    elif mode == 6: 
        radio.receive_timeout(0)
        for i in range(0,3):
            for data in txData:
                radio.transmit(data,True, toAddr)
                time.sleep(0.2)
        radio.receive_timeout(60)
        receiveLoop = threading.Thread(name='radio.receive_hw_int', target=radio.receive_hw_int)
        receiveLoop.start()

    else: # mode = 7

        radio.receive_timeout(0)

        if radio.packetFormat == 'fixed':
            packetFormat = 'variable'
        else:
            packetFormat = 'fixed'        

        radio.set_packet_format(packetFormat=packetFormat,payloadLength=64)
        

        print('Packet Format change to: '+radio.packetFormat)

    
        

radio.receive_timeout(0)
time.sleep(0.5)
IO.output(enablePin, False)
IO.cleanup()
radio.spi.close()
sys.exit()
        
        
