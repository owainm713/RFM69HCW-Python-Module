#!/usr/bin/env python
"""txrx_example3, receiver example program to use with packetradio.py
RFM69HCW packet radio module

created May 7, 2017 OM
last modified - May 9, 2017 OM
last modified - Jan 19, 2020 OM"""

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

#testSendFile = '/home/pi/Documents/yourfilenamehere'     # name/location of file to send - change this to a file on your Pi
#testReceiveFile = '/home/pi/Documents/yourfilenamehere'  # name/location of received file - change this to a file on your Pi

testSendFile = '/home/pi/Documents/PythonProjects/PacketRadio/test.txt'
testReceiveFile = '/home/pi/Documents/PythonProjects/PacketRadio/test2.txt'
#testSendFile = '/home/pi/Documents/PythonProjects/openCVpractice/IMGP3711vSm.jpg'

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

toFile=bytearray()
dataList =[]


def get_radio_data2():
    """get_radio_data2,  version 2"""

    global toFile

    counter = 0

    while checkForInput==True: 
        while len(radio.receiveData) > 0:
                data = radio.receiveData.pop(0)                
                dataList.append(data[3:])                
                counter+=1
                #time.sleep(0.01)
        time.sleep(0.01)


    #print(counter, len(dataList))

    i = 0
    while i <=(len(dataList)-1):
        if dataList[i] == dataList[i-1]:
            del(dataList[i])
        else:
            i+=1

    #print(len(dataList))
        

    for line in dataList:
        #print(line, len(line))
        for char in line:
            #print(char)
            toFile.append(char)

    print('Data in toFile')

    return
                

checkForInput = True
fileLoop = threading.Thread(name='get_radio_data2', target=get_radio_data2)
fileLoop.start()

while True:
    
    mode=int(input("1 - Send file, 2 - Receive file 3 - Stop Receive 4 - convert file 5 - Quit "))

    if mode == 5:
        checkForInput = False
        break

    if mode == 1:
        # convert file to bytearray
        
        with open(testSendFile, 'rb') as textFile:
                f = textFile.read()
                data = bytearray(f)        

        transmitData=[]

        for i in range(0, len(data)-1, 61):
            if (i+61)<=len(data):
                transmitData.append(data[i:i+61])
            else:
                transmitData.append(data[i:])

        #print(len(transmitData))
        success, failed = radio.transmit_with_ack(transmitData,toAddr,intType='hw', retry=4)
        print(success, failed)

    elif mode == 2:
        radio.receive_timeout(-1)
        receiveLoop = threading.Thread(name='radio.receive_sw_int', target=radio.receive_sw_int)
        receiveLoop.start()

    elif mode ==3:
        radio.receive_timeout(0)
        checkForInput = False

    elif mode == 4:
        radio.receive_timeout(0)            
            
        # convert bytearray back to image file

        with open(testReceiveFile, 'wb') as fout:
            fout.write(toFile)
        
        
radio.receive_timeout(0)
IO.output(enablePin, False)
IO.cleanup()
radio.spi.close()
sys.exit()
