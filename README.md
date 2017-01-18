# RFM69HCW-Python-Module
Python 2.x Module for use with the adafruit RFM69HCW breakout board
and the Raspberry Pi

The module uses and relies on py-spidev and python-dev to be installed 
to use the SPI interface. 

The example code also uses RPi.GPIO to set the radio enable and reset 
pins but any python module that can manipulate the Raspberry Pi's 
GPIO could be used instead.

My set up consists of a RaspberryPi3 and PiZero both running Raspbian Jessie.
I'm currently using the 433MHz RFM radios.  The 915MHz version should
run the same and once I get a pair I will verify.

Connections to the RFM69HCW breakout board from the Pi are as follows:

- Pi MISO to Radio MISO
- Pi MOSI to Radio MOSI
- Pi SCLK to Radio SCK
- Pi CE1 to Radio CS
- Pi GPIO ## to Radio EN
- Pi GPIO ## to Radio RST
- Pi 3.3V to Radio VIN
- Pi GND to Radio GND 
- Radio DIO0 to DIO5 - not connected

To operate the radio (via the adafruit breakout board), the Radio EN (enable) pin
has to be high (3.3V) and the Radio RST (reset) pin has to be low (GND). This module
does not use or require the radio's hardware interrupts from DIO0 to DIO5 to operate.
The module does provide for setting the DIO interrupts if you choose to use them.

This python module is set up to use the radio's FSK modulation in packet mode.
I have not tried out the OOK modulation option. The module default radio settings include
- 4800 b/s
- Synch word enable
- 64 byte fixed length packets
- Encyption enabled
- checksum enabled (for trouble shooting disabling this can help)
- address filtering enabled
- 0 dBm transmit power

Tests so far have been limited to using the Pa1 amplifier stage on transmit.

The manufacture (hopeRF) instructions are invaluable and I recommend downloading a copy
to aid in setting up the radio to anything beyond my defaults. These instruction
can be found at www.hoperf.com/upload/rf/RFM69HCW-V1.1.pdf  

