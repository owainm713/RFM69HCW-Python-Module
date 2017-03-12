#!/usr/bin/env python
"""packetradio, module for use with the RFM69HCW packet radio

created Dec 19, 2016 OM
work in progress - Mar 12, 2017"""

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

import time, spidev, sys, threading

class Radio:

    def __init__(self, spi_port, spi_cs):
        """__init__, initialize radio object, setting GPIO pins"""        

        # spi setup

        self.spi=spidev.SpiDev()
        self.spi.open(spi_port,spi_cs)

        # set register list dictionary 

        self.registerList=[]

        # need to add in any registers I didn't deal with..... 

        self.registerList.append({'name' : 'RegOpMode', 'address' : 0x01, 'value' : 0x04})           
        self.registerList.append({'name' : 'RegDataModul', 'address' : 0x02, 'value' : 0x00})     
        self.registerList.append({'name' : 'RegBitRateMsb', 'address' : 0x03, 'value' : 0x1A})
        self.registerList.append({'name' : 'RegBitRateLsb', 'address' : 0x04, 'value' : 0x0B})
        self.registerList.append({'name' : 'RegFdevMsb', 'address' : 0x05, 'value' : 0x00}) 
        self.registerList.append({'name' : 'RegFdevLsb', 'address' : 0x06, 'value' : 0x62})      
        self.registerList.append({'name' : 'RegFrfMsb', 'address' : 0x07, 'value' : 0x6E})
        self.registerList.append({'name' : 'RegFrfMid', 'address' : 0x08, 'value' : 0x10})
        self.registerList.append({'name' : 'RegFrfLsb', 'address' : 0x09, 'value' : 0x00})
        self.registerList.append({'name' : 'RegAfcCtrl', 'address' : 0x0B, 'value' : 0x00})       
        self.registerList.append({'name' : 'RegPaLevel', 'address' : 0x11, 'value' : 0x52})
        self.registerList.append({'name' : 'RegPaRamp', 'address' : 0x12, 'value' : 0x09})
        self.registerList.append({'name' : 'RegOcp', 'address' : 0x13, 'value' : 0x1A})
        self.registerList.append({'name' : 'RegLna', 'address' : 0x18, 'value' : 0x08})
        self.registerList.append({'name' : 'RegRxBw', 'address' : 0x19, 'value' : 0x55})
        self.registerList.append({'name' : 'RegAfcBw', 'address' : 0x1A, 'value' : 0x55})        
        self.registerList.append({'name' : 'RegAfcFei', 'address' : 0x1E, 'value' : 0x14})
        self.registerList.append({'name' : 'RegDioMapping1', 'address' : 0x25, 'value' : 0x40})
        self.registerList.append({'name' : 'RegDioMapping2', 'address' : 0x26, 'value' : 0x07})
        self.registerList.append({'name' : 'RegRssiThresh', 'address' : 0x29, 'value' : 0x8C})
        self.registerList.append({'name' : 'RegRxTimeout1', 'address' : 0x2A, 'value' : 0x00}) 
        self.registerList.append({'name' : 'RegRxTimeout2', 'address' : 0x2B, 'value' : 0x00})
        self.registerList.append({'name' : 'RegPreambleMsb', 'address' : 0x2C, 'value' : 0x00})
        self.registerList.append({'name' : 'RegPreambleLsb', 'address' : 0x2D, 'value' : 0x02})   
        self.registerList.append({'name' : 'RegSyncConfig', 'address' : 0x2E, 'value' : 0x92})
        self.registerList.append({'name' : 'RegSyncValue1', 'address' : 0x2F, 'value' : 0xE4})
        self.registerList.append({'name' : 'RegSyncValue2', 'address' : 0x30, 'value' : 0x7C})
        self.registerList.append({'name' : 'RegSyncValue3', 'address' : 0x31, 'value' : 0xB2})
        self.registerList.append({'name' : 'RegSyncValue4', 'address' : 0x32, 'value' : 0x00})
        self.registerList.append({'name' : 'RegSyncValue5', 'address' : 0x33, 'value' : 0x00})
        self.registerList.append({'name' : 'RegSyncValue6', 'address' : 0x34, 'value' : 0x00})
        self.registerList.append({'name' : 'RegSyncValue7', 'address' : 0x35, 'value' : 0x00})
        self.registerList.append({'name' : 'RegSyncValue8', 'address' : 0x36, 'value' : 0x00})
        self.registerList.append({'name' : 'RegPacketConfig1', 'address' : 0x37, 'value' : 0x14})
        self.registerList.append({'name' : 'RegPayloadLength', 'address' : 0x38, 'value' : 0x40})
        self.registerList.append({'name' : 'RegFifoThresh', 'address' : 0x3C, 'value' : 0x80})
        self.registerList.append({'name' : 'RegPacketConfig2', 'address' : 0x3D, 'value' : 0x03}) 
        self.registerList.append({'name' : 'RegTestPa1', 'address' : 0x5A, 'value' : 0x55})      
        self.registerList.append({'name' : 'RegTestPa2', 'address' : 0x5C, 'value' : 0x70})    
        self.registerList.append({'name' : 'RegTestDagc', 'address' : 0x6F, 'value' : 0x30})
        self.registerList.append({'name' : 'RegTestAfc', 'address' : 0x71, 'value' : 0x00})

        # Node and Broadcast Address registers

        self.registerList.append({'name' : 'RegNodeAdrs', 'address' : 0x39, 'value' : 0x05})
        self.registerList.append({'name' : 'RegBroadcastAdrs', 'address' : 0x3A, 'value' : 0x07})


        # AES Encryption registers

        self.registerList.append({'name' : 'RegAESKey1', 'address' : 0x3E, 'value' : 0x51})
        self.registerList.append({'name' : 'RegAESKey2', 'address' : 0x3F, 'value' : 0x2C})
        self.registerList.append({'name' : 'RegAESKey3', 'address' : 0x40, 'value' : 0xA4})
        self.registerList.append({'name' : 'RegAESKey4', 'address' : 0x41, 'value' : 0xA7})
        self.registerList.append({'name' : 'RegAESKey5', 'address' : 0x42, 'value' : 0xB4})
        self.registerList.append({'name' : 'RegAESKey6', 'address' : 0x43, 'value' : 0xD4})
        self.registerList.append({'name' : 'RegAESKey7', 'address' : 0x44, 'value' : 0xA4})
        self.registerList.append({'name' : 'RegAESKey8', 'address' : 0x45, 'value' : 0xAE})
        self.registerList.append({'name' : 'RegAESKey9', 'address' : 0x46, 'value' : 0xA4})
        self.registerList.append({'name' : 'RegAESKey10', 'address' : 0x47, 'value' : 0xF4})
        self.registerList.append({'name' : 'RegAESKey11', 'address' : 0x48, 'value' : 0xA3})
        self.registerList.append({'name' : 'RegAESKey12', 'address' : 0x49, 'value' : 0xD4})
        self.registerList.append({'name' : 'RegAESKey13', 'address' : 0x4A, 'value' : 0xA6})
        self.registerList.append({'name' : 'RegAESKey14', 'address' : 0x4B, 'value' : 0x44})
        self.registerList.append({'name' : 'RegAESKey15', 'address' : 0x4C, 'value' : 0x72})
        self.registerList.append({'name' : 'RegAESKey16', 'address' : 0x4D, 'value' : 0x29})

        for reg in self.registerList:
            self.single_access_write(reg['address'], reg['value'])
            time.sleep(0.01)  # time delay required or freq doesn't set correctly

        # for testing print register contents

        """for reg in self.registerList:
            print(hex(reg['address']),' ',hex(self.single_access_read(reg['address'])))"""

        self.temperatureOffset = 0
        self.receiveData=[] # list to place received data
        self.receiveTimeout = 0 # timeout value for the receiver

        return

    def single_access_write(self, reg=0x01, regValue=0x0):
        """single_access_write, function to write to a single data register
        of the RFM69HCW

        Default register to write to is RegOpMode"""    

        dataTransfer=self.spi.xfer2([(1<<7)+reg,regValue])        

        return

    def single_access_read(self, reg=0x00):
        """single_access_read, function to read a single data register
        of the RFM69HCW

        Default register to read is fifo"""

        dataTransfer=self.spi.xfer2([(0<<7)+reg,0])         

        return dataTransfer[1]


    def read_all_registers(self):
        """read_all_registers, function to read all the registers"""

        for register in range(0,80):
            print(hex(register),hex(self.single_access_read(register)))

        for reg in self.registerList:
            print(reg['name'],hex(reg['value']))

        return

    def variable_length_write(self, reg=0x0, length=1, regValues=[]):
        """variable_length_write, function to write multiple consecutive
        bytes of data to the radio on a single spi transaction"""

        # do I need the length variable for anything!!!???

        writeData=[(1<<7)+reg]
        writeData.extend(regValues)

        dataTransfer=self.spi.xfer2(writeData)

        return

    def fifo_write(self, fifoData, addressOn=False, address=0,packetLength=64):
        """fifo_write, function to write data to the radio fifo register,
        this will be the data that gets transmitted by the radio

        fifoData  contains a string that will be converted to a bytearray for transmitting
        packetLength is the packet length to be transmitted"""

        fifoData=bytearray(fifoData)

        if addressOn==True:
            fifoData.insert(0,address) # address byte

        # check fifoData length, if less than packetLength, add spaces for padding
        # until fifoData length is equal to packetLength

        if len(fifoData)<packetLength:
            for i in range(len(fifoData),packetLength):
                fifoData.append(' ')

        # check fifoData length, if greater than packetLength, remove excess data
        # until fifoData length is equal to packetLength

        if len(fifoData)>packetLength:
            fifoData=fifoData[0:packetLength]       

        # write data to fifo register    

        self.variable_length_write(0x0,packetLength,fifoData)

        return

    def fifo_read(self):
        """fifo_read, function to read data from the radio fifo register,
        this will be the data that was received by the radio"""

        fifoData=bytearray()

        # check FifoNotEmpty flag in RegIrqFlags2 0x28
        # read data until fifo is empty

        while (self.single_access_read(0x28) & 0b01000000)==64:            
            fifoData.append(self.single_access_read())        

        return fifoData

    def transmit_packet(self):
        """transmit_packet, function to transmit a single packet of data that
        has been preloaded into fifo and put the radio into standby mode upon
        completion"""

        # put radio into transmit mode

        self.set_operating_mode('transmit')
        #self.single_access_write(0x01,0x0C)  # 0b00001100 - transmit mode

        # check that the packet has been sent

        count=0

        while (self.single_access_read(0x28) & 0b00001000)!=8:
            count+=1
            if count == 100:                
                break
            time.sleep(0.025)

        # put radio back into standby mode

        self.set_operating_mode('standby')
        #self.single_access_write(0x01,0x04)  # 0b0000100 - standby mode        

        return

    def last_rssi(self):
        """last_rssi, user function to get the last rssi value
        mesaured by the radio receiver"""

        lastRssi=-self.single_access_read(0x24)/2

        return lastRssi        

    def receive(self,timeout=999, background=False):
        """receive, user function to put the radio into receive
        mode"""

        # set timeout value,  a value of -1 will let the receiver run
        # indefinately

        self.receiveTimeout=timeout

        def receive_thread():
            """receive_thread, internal function for putting the radio into receive mode, this
            can be threaded to move the receive function into the background"""

            # put radio into receive mode

            self.set_operating_mode('receive')
            #self.single_access_write(0x01,0x10)  # 0b00010000 - receive mode

            timerStart=time.time()
            
            while time.time()<=(timerStart+self.receiveTimeout) or self.receiveTimeout == -1:

                # check for received data via payload ready flag

                while (self.single_access_read(0x28) & 0b00000100)==4:
                    self.receiveData.append(self.fifo_read())

                time.sleep(0.1)

            # put radio back into standby mode

            self.set_operating_mode('standby')
            #self.single_access_write(0x01,0x04)  # 0b0000100 - standby mode

            return self.receiveData

        # check whether or not the receive function is to be put into the background
        # (threaded) or stay in the foreground (inline)

        if background == True:
            receiveLoop=threading.Thread(name='receive_thread',target=receive_thread)
            receiveLoop.start()
            return
        else:
            receive_thread()
            return self.receiveData

    def set_address_filtering(self, mode='none'):
        """set_address_filtering, user function to set the addressing
        filtering mode; none (none), node address match (node), either node or broadcast
        address match (both)"""

        if mode == 'node':
            addressBits = 0b01
        elif mode == 'both':
            addressBits = 0b10
        else:
            addressBits = 0b00
        
        regPacketConfig = self.single_access_read(0x37)        
        regPacketConfig = regPacketConfig & 0b11111001        
        regPacketConfig = regPacketConfig | (addressBits<<1)        
        self.set_register_by_name('RegPacketConfig1', regPacketConfig)

        return       
   

    def set_afc(self, afcLowBetaOn='Standard', afcOffset=0, dccFreq=4, rxBW=10.4, autoclearOn='off', autoOn='on'):
        """set_afc, user function to set the parameters for automatic
        frequency correction, this will set 4 different registers, RegAfcCtrl,
        RegAfcBw and RegAfcFei, RegTestAfc"""

        #------ RegAfcCtrl and RegTestAfc Section ----------

        if afcLowBetaOn == 'Improved':
            self.set_register_by_name('RegAfcCtrl', 0x20)
            afcOffsetReg = afcOffset/488
            self.set_register_by_name('RegTestAfc', afcOffsetReg)            

        else:  # afcLowBetaOn = Standard
            self.set_register_by_name('RegAfcCtrl', 0x00)            

        #-------- RegAfcBw Section ----------

        dccFreqOptions = [(16,0b000),(8,0b001),(4,0b010),(2,0b011),
                          (1,0b100),(0.5,0b101),(0.25,0b110),(0.125,0b111)]

        dccBits = 0b010 # default value if a correct match is not found

        for dcc in dccFreqOptions:
            if dcc[0] == dccFreq:
                dccBits = dcc[1]    

        rxBwOptions = [(2.6,0b10111),(3.1,0b01111),(3.9,0b00111),(5.2,0b10110),
                       (6.3,0b01110),(7.8,0b00110),(10.4,0b10101),(12.5,0b01101),
                       (15.6,0b00101),(20.8,0b10100),(25,0b01100),(31.3,0b00100),
                       (41.7,0b10011),(50.0,0b01011),(62.5,0b00011),(83.3,0b10010),
                       (100.0,0b01010),(125.0,0b00010),(166.7,0b10001),(200.0,0b01001),
                       (250.0,0b00001),(333.3,0b10000),(400.0,0b01000),(500.0,0b00000)]

        bwBits = 0b10101 # default value if a correct match is not found

        for bw in rxBwOptions:
            if bw[0] == rxBW:
                bwBits = bw[1]

        afcBwReg = (dccBits<<5)+bwBits
        self.set_register_by_name('RegAfcBw', afcBwReg)
        
        #--------- RegAfcFei Section ------------

        if autoclearOn == 'off':
            autoclearBits = 0b0
        else:
            autoclearBits = 0b1

        if autoOn == 'on':
            autoOnBits = 0b1
        else:
            autoOnBits = 0b0

        afcFeiReg=(autoclearBits<<3) + (autoOnBits<<2)
        self.set_register_by_name('RegAfcFei', afcFeiReg)          

        return

    def set_auto_rx_restart(self, autoRestartOn='on', interPacketDelay=0x0):
        """set_auto_rx_restart, user function to enable/disable
        the automatic Rx restart (RSSI phase) feature of the radio
        and set the InterPacketRxDelay"""

        if autoRestartOn == 'off':
            autoRestartOnBit = 0b0
        else: # autoRestartOn = on
            autoRestartOnBit = 0b1

        if interPacketDelay < 0 or interPacketDelay > 15:
            interPacketDelay = 0
           
        regPacketConfig = self.single_access_read(0x3D)        
        regPacketConfig = regPacketConfig & 0b00001101        
        regPacketConfig = regPacketConfig | (interPacketDelay<<4) + (autoRestartOnBit<<1)        
        self.set_register_by_name('RegPacketConfig2', regPacketConfig)

        return

    def set_bitrate(self,bitrate):
        """set_bitrate, user function to change the radio
        transmission bitrate"""

        bitrate=int(32000000/bitrate)

        msb = (bitrate & 0xFF00)>>8
        lsb = bitrate & 0xFF

        self.variable_length_write(0x03, 2,[msb,lsb])

        for reg in self.registerList:
            if reg['name'] == 'RegBitRateMsb':                
                reg['value']= msb            
            elif reg['name'] == 'RegBitRateLsb':                
                reg['value']= lsb
            else:
                pass        

        return

    def set_broadcast_address(self, address=0x07):
        """set_broadcast_address, user function to set the broadcast
        address of the current radio"""

        address = address & 0xFF # check to ensure address is only 8 bits long      
        self.set_register_by_name('RegBroadcastAdrs', address)

        return

    def set_checksum(self, crcOn='on', autoClearFifo='on'):
        """set_checksum, user function to enable a checksum
        calculation function."""

        if crcOn == 'off':
            crcOnBit = 0b0
        else:
            crcOnBit = 0b1

        if autoClearFifo == 'off':
            autoClearBit = 0b1
        else:
            autoClearBit = 0b0
        
        regPacketConfig = self.single_access_read(0x37)        
        regPacketConfig = regPacketConfig & 0b11100111        
        regPacketConfig = regPacketConfig | ((crcOnBit<<4)+(autoClearBit<<3))        
        self.set_register_by_name('RegPacketConfig1', regPacketConfig)

        return

    def set_data_mode(self, dataMode='packet', modulationType='FSK', modShaping='none', bitSynchOn='on'):
        """set_data_mode, function to set the data mode parameters"""

        if dataMode == 'continuous':
            if bitSynchOn == 'off':
                dataModeBits = 0b11
            else: # bitSynchOn = on
                dataModeBits = 0b10
        else: # dataMode = packet
            dataModeBits = 0b00

        if modulationType == 'OOK':
            modTypeBits = 0b01

            if modShaping == 1:
                modShapingBits = 0b01  # filtering with fcutoff = BR
            elif modShaping == 2:
                modShapingBits = 0b10  # filtering with fcutoff = 2*BR        
            else: # modShaping = none
                modShapingBits = 0b00
            
        else: # modulationType = FSK
            modTypeBits = 0b00

            if modShaping == 1:
                modShapingBits = 0b01  # Guassian filter, BT = 1
            elif modShaping == 0.5:
                modShapingBits = 0b10  # Gaussian filter, BT = 0.5
            elif modShaping == 0.3:
                modShapingBits = 0b11  # Gaussian filter, BT = 0.3
            else: # modShaping = none
                modShapingBits = 0b00


        regDataMode = (dataModeBits<<5) + (modTypeBits<<3) + modShapingBits
        self.set_register_by_name('RegDataModul', regDataMode)

        return 

    def set_dc_free_encoding(self, encodingType='none'):
        """set_dc_free_encoding, user function to enable/disable
        DC free encoding, 3 choices - none, manchester or whitening"""

        if encodingType == 'manchester':
            encodingBits = 0b01
        elif encodingType == 'whitening':
            encodingBits = 0b10
        else : # encodingType = none
            encodingBits = 0b00
        
        regPacketConfig = self.single_access_read(0x37)        
        regPacketConfig = regPacketConfig & 0b10011111        
        regPacketConfig = regPacketConfig | (encodingBits<<5)        
        self.set_register_by_name('RegPacketConfig1', regPacketConfig)

        return

    def set_dio(self, dio0=0, dio1=0, dio2=0, dio3=0, dio4=0, dio5=0, clkOut='off'):
        """set_dio, user function to map the DIO (digital I/O) pins of
        the radio as well as set the clock output frequency if used"""

        dioList = [dio0, dio1, dio2, dio3, dio4, dio5]

        # check to ensure dio entered is a valid dio mapping value
        # i.e. within 0 (0b00) to 3 (0b11)

        for i in range(0,6):
            if dioList[i] < 0 or dioList[i] > 3:
                dioList[i] = 0

        # set clock output bits

        if clkOut == 1:
            clkOutBits = 0b000  # FXOSC
        elif clkOut == 2:
            clkOutBits = 0b001  # FXOSC/2
        elif clkOut == 4:
            clkOutBits = 0b010  # FXOSC/4
        elif clkOut == 8:
            clkOutBits = 0b011  # FXOSC/8
        elif clkOut == 16:
            clkOutBits = 0b100  # FXOSC/16
        elif clkOut == 32:
            clkOutBits = 0b101  # FXOSC/32
        elif clkOut == 'auto':
            clkOutBits = 0b110  # RC(autmatically enabled)
        else: # clkOut = off
            clkOutBits = 0b111  # Off

        regDio1 = (dioList[0]<<6) + (dioList[1]<<4) + (dioList[2]<<2) + dioList[3]
        regDio2 = (dioList[4]<<6) + (dioList[5]<<4) + clkOutBits
        self.set_register_by_name('RegDioMapping1', regDio1)
        self.set_register_by_name('RegDioMapping2', regDio2)        

        return
    
    def set_encryption(self, aesOn='on', aesKeyList=[]):
        """set_encryption, user function to enable/disable AES encryption
        and set the 16 AES encyption key registers. If aesKeyList is left empty
        the AES key registers will be left as is"""

        #---- RegPacketConfig2 section (AES enable/disable -------

        if aesOn == 'off':
            aesOnBit = 0b0
        else: # aesOn = on
            aesOnBit = 0b1
        
        regPacketConfig = self.single_access_read(0x3D)        
        regPacketConfig = regPacketConfig & 0b11111110       
        regPacketConfig = regPacketConfig | aesOnBit        
        self.set_register_by_name('RegPacketConfig2', regPacketConfig)

        #-----RegAesKey1 through 16 section -------------

        if len(aesKeyList)>0: # if aesKeyList is empty, leave values as is

            # Check length of aesKeyList and add or delete items as
            # required to make the length 16
                
            while len(aesKeyList) !=16:
                if len(aesKeyList) < 16:
                    aesKeyList.append(0xB3)
                else:
                    aesKeyList.pop()

            self.variable_length_write(0x3E, 13, aesKeyList)

            regAddrs=0x3E
            for i in range(0,16):
                for reg in self.registerList:
                    if reg['address'] == regAddrs:                
                        reg['value']= aesKeyList[i]            
                regAddrs+=1     

        return

    def set_fifo_threshold(self, txStartCond='FifoLevel', threshold=20):
        """set_fifo_threshold, user function to define the condition
        to start packet transmission and set the Fifo threshold used to
        trigger the FifoLevel interrupt"""

        if txStartCond == 'FifoLevel':
            txStartBit = 0b0
        else: #TxStartCond = FifoNotEmpty
            txStartBit = 0b1

        if abs(threshold) > 66: # ensure threshold isn't bigger than the Fifo (66 bytes)
            threshold = 66

        regFifoThresh = (txStartBit<<7)+threshold
        self.set_register_by_name('RegFifoThresh', regFifoThresh)

        return

    def set_frequency(self,frequency):
        """set_frequency, user function to change the radio
        frequency"""

        frequency=int(frequency/61.03515625)        

        msb = (frequency & 0xFF0000)>>16
        mid = (frequency & 0xFF00)>>8
        lsb = frequency & 0xFF

        self.variable_length_write(0x07, 3,[msb,mid,lsb])        

        for reg in self.registerList:
            if reg['name'] == 'RegFrfMsb':                
                reg['value']= msb
            elif reg['name'] == 'RegFrfMid':                
                reg['value']= mid
            elif reg['name'] == 'RegFrfLsb':                
                reg['value']= lsb
            else:
                pass
                        
        return

    def set_frequency_deviation(self,fDev):
        """set_frequency_deviation, user function to change the radio
        transmission frequency deviation"""

        fDev=int(fDev/61.03515625)

        msb = (fDev & 0xFF00)>>8
        lsb = fDev & 0xFF
        
        self.variable_length_write(0x05, 2,[msb,lsb])

        for reg in self.registerList:
            if reg['name'] == 'RegFdevMsb':                
                reg['value']= msb            
            elif reg['name'] == 'RegFdevLsb':                
                reg['value']= lsb
            else:
                pass 

        return

    def set_lna(self, autoOn='on', gainSelect='G1', inputZ=50):
        """set_lna, user function to set the parameters for the
        receiver's LNA (low noise amplifier)"""

        if inputZ == 50:
            zBit = 0b0
        else:  # inputZ = 200
            zBit = 0b1

        gainOptions =[('G1',0b001),('G2',0b010),('G3',0b011),('G4',0b100),
                      ('G5',0b101),('G6',0b110)]

        gainBits = 0b001 # default value if a correct match is not found

        if autoOn == 'off':
            for gain in gainOptions:
                if gain[0] == gainSelect:
                    gainBits = gain[1]

            lnaReg = (zBit<<7)+ gainBits

        else:
            lnaReg = zBit<<7

        self.set_register_by_name('RegLna', lnaReg)
        
        return

    def set_mode_sequencer(self, sequencer='on'):
        """set_mode_sequencer, user function to enable/disable the
        radio's automatic sequencer"""

        if sequencer == 'off':
            sequencerBit= 0b1
        else: # sequencer = 'on'
            sequencerBit = 0b0
        
        regOpMode = self.single_access_read(0x01)        
        regOpMode = regOpMode & 0b01111111        
        regOpMode = regOpMode | (sequencerBit<<7)        
        self.set_register_by_name('RegOpMode', regOpMode)  

        return

    def set_node_address(self, address=0x05):
        """set_node_address, user function to set the node address
        of the current radio"""

        address = address & 0xFF # check to ensure address is only 8 bits long        
        self.set_register_by_name('RegNodeAdrs', address)

        return

    def set_OCP(self, ocpOn='on', ocpMax=95):
        """set_OCP, user function to enable/disable OCP (Over Current
        Protection) and set the max current (mA)"""

        if ocpOn =='off':
            ocpOnBit = 0b0
        else: #ocpOn = on
            ocpOnBit = 0b1

        if ocpMax > 120:
            ocpMax = 120
        elif ocpMax < 45:
            ocpMax = 45

        ocpTrimBits = int((ocpMax-45)/5)       

        regOCP = (ocpOnBit<<4) + ocpTrimBits        
        self.set_register_by_name('RegOcp', regOCP)

        return

    def set_operating_mode(self, mode='standby'):
        """set_operating_mode, user function to set the radio's current
        mode; transmit, receive, sleep, standby and freqSynth."""

        if mode == 'transmit':
            modeBits = 0b011
        elif mode == 'receive':
            modeBits = 0b100
        elif mode == 'sleep':
            modeBits = 0b000
        elif mode == 'freqSynth':
            modeBits = 0b010
        else: #mode = standby
            modeBits = 0b001
       
        regOpMode = self.single_access_read(0x01)        
        regOpMode = regOpMode & 0b11100011        
        regOpMode = regOpMode | (modeBits<<2)        
        self.set_register_by_name('RegOpMode', regOpMode)    

        return   

    def set_packet_format(self, packetFormat='fixed',payloadLength=64):
        """set_packet_format, user function to set the packet format
        including fixed vs variable vs unlimited length and payload length.
        This sets part of RegPacketConfig1 and all of RegPayloadLength"""

        #----- RegPacketConfig1 Section ---------

        if packetFormat == 'variable':
            packetFormatBit = 0b1
        else: # packetFormat = fixed or unlimited
            packetFormatBit = 0b0
        
        regPacketConfig = self.single_access_read(0x37)        
        regPacketConfig = regPacketConfig & 0b01111111        
        regPacketConfig = regPacketConfig | (packetFormatBit<<7)        
        self.set_register_by_name('RegPacketConfig1', regPacketConfig)

        #----- RegPayloadLength Section -------

        payloadLength = abs(payloadLength)

        if packetFormat != 'unlimited':
            if payloadLength > 255:
                payloadLength = 255
        else:
            payloadLength = 0        

        self.set_register_by_name('RegPayloadLength', payloadLength)

        return
    

    def set_power(self,ampSelect, powerLevel, powerRamp=40):
        """set_power, user function to choose the power amplifier(s),
        transmit power used and power ramp time, this will set the following
        2 registers, RegPaLevel and RegPaRamp"""

        #------ RegPaLevel Section ----------

        ampSelectBits=0
        powerLevelBits=0

        if ampSelect == 'Pa0':
            """ haven't been able to get Pa0 working"""
            ampSelectBits=0b100
            
            if powerLevel <-18 or powerLevel >13:
                powerLevel = -18

            powerLevelBits = 18 + int(powerLevel)
            
        elif ampSelect == 'Pa2' or ampSelect =='Pa2H' :
            ampSelectBits=0b011

            if ampSelect == 'Pa2':

                if powerLevel <2 or powerLevel >17:
                    powerLevel = 2            
            
                powerLevelBits = 14 + int(powerLevel)

            if ampSelect == 'Pa2H':

                if powerLevel <5 or powerLevel >20:
                    powerLevel = 5            
            
                powerLevelBits = 11 + int(powerLevel)

                # high power output requires different handling and other registers changes
                # such as TestPa1, TestPa2 &  TestAfc                
            
        else:
            ampSelectBits=0b010  # default to Pa1

            if powerLevel <-2 or powerLevel >13:
                powerLevel = -2            
            
            powerLevelBits = 18 + int(powerLevel)

        powerRegister=(ampSelectBits<<5)+powerLevelBits

        self.set_register_by_name('RegPaLevel',powerRegister)

        #------ RegPaRamp Section -----------

        paRampOptions = [(3400,0b0000),(2000,0b0001),(1000,0b0010),(500,0b0011),
                         (250,0b0100),(125,0b0101),(100,0b0110),(62,0b0111),
                         (50,0b1000),(40,0b1001),(31,0b1010),(25,0b1011),
                         (20,0b1100),(15,0b1101),(12,0b1110),(10,0b1111)]

        rampReg = 0b1001 # default value if a correct match is not found

        for ramp in paRampOptions:
            if ramp[0] == powerRamp:
                rampReg = ramp[1]

        self.set_register_by_name('RegPaRamp',rampReg)         

        return

    def set_preamble_length(self, length=2):
        """set_preamble_length, user function to set the length
        of the preamble (bytes)"""

        msb = (length & 0xFF00)>>8
        lsb = length & 0xFF

        self.variable_length_write(0x2C, 2,[msb,lsb])

        for reg in self.registerList:
            if reg['name'] == 'RegPreambleMsb':                
                reg['value']= msb            
            elif reg['name'] == 'RegPreambleLsb':                
                reg['value']= lsb
            else:
                pass        

        return

    def set_register_by_address(self, registerAddr, value):
        """set_register_by_address, user function to set a single
        register by passing the register name amd value for it to be
        set to. The radio object registerList is also updated"""

        for reg in self.registerList:
            if reg['address'] == registerAddr:
                self.single_access_write(reg['address'], value)
                reg['value']=value
                break

        return

    def set_register_by_name(self, registerName, value):
        """set_register_by_name, user function to set a single
        register by passing the register name amd value for it to
        be set to. The radio object registerList is also updated"""

        for reg in self.registerList:
            if reg['name'] == registerName:
                self.single_access_write(reg['address'], value)
                reg['value']=value
                break

        return

    def set_rssi_threshold(self, rssi):
        """set_rssi_threshold, user funstion to change the receive
        signal strength indicator (rssi) threshold (dBm) used by the
        receiver"""

        rssi = int(abs(rssi)*2)

        self.set_register_by_name('RegRssiThresh',rssi)        

        return

    def set_rxbw(self, dccFreq=4, rxBW=10.4):
        """set_rxbw, user function to set the receiver bandwidth
        parameters when afc (automatic frequency correction) is not
        enabled"""

        dccFreqOptions = [(16,0b000),(8,0b001),(4,0b010),(2,0b011),
                          (1,0b100),(0.5,0b101),(0.25,0b110),(0.125,0b111)]

        dccBits = 0b010 # default value if a correct match is not found

        for dcc in dccFreqOptions:
            if dcc[0] == dccFreq:
                dccBits = dcc[1]    

        rxBwOptions = [(2.6,0b10111),(3.1,0b01111),(3.9,0b00111),(5.2,0b10110),
                       (6.3,0b01110),(7.8,0b00110),(10.4,0b10101),(12.5,0b01101),
                       (15.6,0b00101),(20.8,0b10100),(25,0b01100),(31.3,0b00100),
                       (41.7,0b10011),(50.0,0b01011),(62.5,0b00011),(83.3,0b10010),
                       (100.0,0b01010),(125.0,0b00010),(166.7,0b10001),(200.0,0b01001),
                       (250.0,0b00001),(333.3,0b10000),(400.0,0b01000),(500.0,0b00000)]

        bwBits = 0b10101 # default value if a correct match is not found

        for bw in rxBwOptions:
            if bw[0] == rxBW:
                bwBits = bw[1]

        rxBwReg = (dccBits<<5)+bwBits
        self.set_register_by_name('RegRxBw', rxBwReg)        

        return

    def set_sync(self, syncOn='on', syncSize=3, syncTol=2, fifoFill=0):
        """set_sync, user function to set the sync word options.
        This will set the RegSyncConfig register """
    
        if syncOn == 'off':
            syncOnBit = 0b0
        else:
            syncOnBit = 0b1

        if abs(syncSize) > 8:
            syncSize = 8

        syncSizeBits = syncSize-1

        if abs(syncTol) > 7:
            syncTol = 7

        syncConfigReg = (syncOnBit<<7) + (fifoFill<<6) + (syncSizeBits<<3) + syncTol
        self.set_register_by_name('RegSyncConfig', syncConfigReg)                      
        
        return

    def set_sync_word(self, syncValueList=[0xE2,0x4A,0x26]):
        """set_sync_word, user function to set the sync word.
        This will set the 8 RegSyncValue registers"""    

        # Check length of syncValue list and add or delete items as
        # required to make the length 8
        
        while len(syncValueList) !=8:
            if len(syncValueList) < 8:
                syncValueList.append(0x0)
            else:
                syncValueList.pop()

        self.variable_length_write(0x2F, 8, syncValueList)

        regAddrs=0x2F

        for i in range(0,len(syncValueList)):
            for reg in self.registerList:
                if reg['address'] == regAddrs:                
                    reg['value']= syncValueList[i]            
            regAddrs+=1         
        
        return  

    def set_temperature_offset(self, offset=0):
        """set_temperature_offset, user function to change the
        temperature offset value, used to calibrate the sensor reading"""

        self.temperatureOffset = offset

        return

    def set_timeout_rssi_threshold(self, timeoutOn='off', multiplier=0x00):
        """set_time_rssi_threshold, user function enable/disable the
        TimeoutRssiThresh interrupt and to set it's level if enabled"""

        if timeoutOn == 'on':
            if multiplier > 0 and multiplier < 256:
                timeoutBits = multiplier
            else:
                timeoutBits = 0b11111111
        else: # timeoutOn = off
            timeoutBits = 0b0

        #print(bin(timeoutBits))
        self.set_register_by_name('RegRxTimeout2', timeoutBits)
        
        return


    def set_timeout_rx_start(self, timeoutOn='off', multiplier=0x00):
        """set_time_rx_start, user function enable/disable the
        TimeoutRxStart interrupt and to set it's level if enabled"""

        if timeoutOn == 'on':
            if multiplier > 0 and multiplier < 256:
                timeoutBits = multiplier
            else:
                timeoutBits = 0b11111111
        else: # timeoutOn = off
            timeoutBits = 0b0
        
        self.set_register_by_name('RegRxTimeout1', timeoutBits)
        
        return

    def temperature(self):
        """temperature, user function to get the temperature reading from the
        radio's temperature sensor

        registers 0x4E and 0x4F relate to the temperature sensor"""

        # radio has to be in either Stand by or freq synth mode to take temperature

        writeData=0b1001  # bit sequence required to start taking temp reading

        self.single_access_write(reg=0x4E, regValue=writeData)

        while self.single_access_read(reg=0x4E)==5:  # 5 = 0b101
            pass

        tempSensorValue=self.single_access_read(reg=0x4F)

        # using tempSensorValue of 150 equaling 20 degrees
        # and tempSensor range from -40 to 85 degrees

        temperature=-40+((210+self.temperatureOffset)-tempSensorValue)    

        return temperature

    def transmit(self, transmitData, addressOn=False, address=0,packetLength=64):
        """transmit, user function to transmit data """

        self.fifo_write(transmitData, addressOn, address, packetLength)
        self.transmit_packet()

        return



if __name__=='__main__':

    import RPi.GPIO as IO
    import time, sys

    mode='Tx'

    enablePin = 26
    resetPin = 19

    # set up GPIO settings
    IO.setwarnings(False)
    IO.setmode(IO.BCM)

    IO.setup(enablePin, IO.OUT)
    IO.output(enablePin, False)
    IO.setup(resetPin, IO.OUT)
    IO.output(resetPin, False)

    # testing area

    IO.output(enablePin, True)    
    radio=Radio(0,1)


    #radio.set_frequency(440000000)
    #radio.set_bitrate(19196)
    #radio.set_frequency_deviation(7500)
    radio.set_power('Pa1',-2, 40)
    #radio.set_rssi_threshold(-65)
    #radio.set_afc('Improved', 7320, .125, 10.4, 'on', 'on')
    #radio.set_rxbw(0.5, 62.5)
    #radio.set_lna('off', 'G5', 200)
    #radio.set_preamble_length(300)
    #radio.set_sync('on', 5, 6, 0)
    #radio.set_sync_word([0xD4,0x27,0x9A])
    #radio.set_checksum('on','on')
    #radio.set_address_filtering('node')
    #radio.set_node_address(0x09)
    #radio.set_broadcast_address(0x0A)
    #radio.set_fifo_threshold('FifoNotEmpty', 7)
    #radio.set_encryption('off' ,[0x3F,0x72,0x48, 0xB1, 0x3F,0x72,0x48, 0xB1,0x3F,0x72,0x48, 0xB1])
    #radio.set_dc_free_encoding('manchester')
    #radio.set_packet_format('unlimited', 128)
    #radio.set_OCP('on', 95)
    #radio.set_data_mode('continuous', 'OOK',2, 'off')
    #radio.set_dio(dio5=3)
    #radio.set_timeout_rx_start('off', 234)
    #radio.set_timeout_rssi_threshold('off', 234)
    #radio.set_auto_rx_restart('on', 12)
    
    radio.set_temperature_offset(-3)
    print(radio.temperature())

    def print_radio_data():
        """print_radio_data"""
        
        while len(radio.receiveData) > 0:
            data=radio.receiveData.pop(0)                
            print(data)            

        return                

    if mode =='Tx':

        for i in range(0,1):            
            radio.transmit('2x Houston we have lift off, repeat we have lift off', addressOn=True, address=5,packetLength=64)
            time.sleep(0.125)
            radio.transmit('set_datamode mmm packet vs ook etc m not as important until I ha', addressOn=True, address=5,packetLength=64)
            time.sleep(0.125)

        #radio.set_register_by_name('RegNodeAdrs',0x0B)
        #radio.read_all_registers()

        #radio.set_register_by_address(0x39,0x05)
        #radio.set_operating_mode('transmit')
        #radio.set_mode_sequencer('on')
        radio.read_all_registers()
        
    else: # Rx mode test area

        # example with receive function put in the background via threading
        
        radio.receive(5, True)  
        for i in range(0,15):
            print(i)
            print_radio_data()            
            time.sleep(1)               

        # example with receive function in the foreground

        print('Going to 2nd receive mode')

        radio.receiveData=[]
        radioData=radio.receive(10)

        for line in radioData:
            print(line)

        # example with receive function put in the background via threading
        # timeout set to -1 for never off

        print('Going to 3rd receive mode')

        radio.receiveData=[]        
        radio.receive(-1, True)  
        for i in range(0,25):
            print(i)
            print_radio_data()            
            time.sleep(1)
        radio.receiveTimeout = 0 # stop the receiver by forcing the timer to expire
        time.sleep(1) # need to add delay to allow thread to catch up

        print('Going to 4th receive mode')
        radio.receiveData=[]         
        radioData=radio.receive(10)

        for line in radioData:
            print(line) 

        print(radio.last_rssi())       

    
    IO.output(enablePin, False)
    IO.cleanup()
    radio.spi.close()
    


    
