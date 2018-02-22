#!/usr/bin/python

# MIT License
# 
# Copyright (c) 2017 Arkadiusz Netczuk <dev.arnet@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


## 
## Pinout ATtiny85 -> RPi:
##      SCK (pin7)    -> SCLK-GPIO11 (pin23) - IN mode
##      DO  (pin6)    -> MISO-GPIO9  (pin21) - IN mode
##      DI  (pin5)    -> M0SI-GPIO10 (pin19) - OUT mode
##
##      DO/DI area crossed with MISO/M0SI to keep compatibility with MCU programmer
##



if __name__ != '__main__':
    print "Not in main - exiting"
    exit(1);



import RPi.GPIO as GPIO

import sys, traceback
import Queue


PIN_SCK=11      ## SCLK-GPIO11 (pin23)
PIN_DI=9        ## MISO-GPIO9  (pin21)
PIN_DO=10       ## M0SI-GPIO10 (pin19)
PIN_SS=22       ## GPIO12      (pin15)


bucket = Queue.Queue()




class SlaveState:
    IDLE = 1
    SENDING_VALUE = 2
    RECEIVING_ECHO = 3


class SpiSlave(object):
    def __init__(self):
        self.unknownState = True
        self.state = SlaveState.IDLE
        
        self.receiveBuffer = 0
        self.edgeCunter = 0
        self.sendBuffer = 0
        self.counter = 0
        
        self.pinSCK = 0
        self.pinDI = 0


    ## called on fallind edge of last bit
    def receivedByte(self):
        ## received full byte

        ###print "received byte: {0:#010b}".format(self.receiveBuffer)

        if self.state == SlaveState.IDLE:
            if self.receiveBuffer == 0b10101010:
                ## send echo message
                self.sendBuffer = self.counter
                print "echo command -- sending echo request: {0:#010b}".format(self.sendBuffer)
                self.state = SlaveState.SENDING_VALUE
                self.slaveSelected()
        
        elif self.state == SlaveState.SENDING_VALUE:
            ## sending done -- received trash
            print "sending completed -- receiving echo"
            self.state = SlaveState.RECEIVING_ECHO
            
        elif self.state == SlaveState.RECEIVING_ECHO:
            ## echo received
            print "echo received: {0:#010b}".format(self.receiveBuffer)
            self.state = SlaveState.IDLE
            self.counter += 1


    def sendBit(self):
        if self.state != SlaveState.SENDING_VALUE:
            return
            
        ##print "sending: ", self.edgeCunter, self.sendBuffer
            
        ## sending bit
        self.sendBuffer = (self.sendBuffer << 1)
        bit = 0;
        if (self.sendBuffer & 0x100) != 0:
            bit = 1
        GPIO.output(PIN_DO, bit)


    def receiveBit(self):
        self.pinDI = GPIO.input(PIN_DI)
        self.receiveBuffer = (self.receiveBuffer << 1) & 0xFF | self.pinDI
        ##print "received edge: {} pin: {} {:#010b}".format(self.edgeCunter, self.pinDI, self.receiveBuffer)


    ## Define a threaded callback function to run in another thread when events are detected  
    def clock_tick(self, channel):
        ## Needed to modify global copy of globvar
        global bucket
        
        try:
            self.pinSCK = GPIO.input(PIN_SCK)
            if self.unknownState:
                self.handleUnknownState()                    
                return

            if self.pinSCK == 0:
                self.sendBit()
            else:
                self.receiveBit()

            if self.edgeCunter < 15:
                self.edgeCunter += 1
                return

            ## received last falling edge
            self.receivedByte()
            self.edgeCunter = 0
            self.receiveBuffer = 0

        except:
            bucket.put(sys.exc_info())
    

    def handleUnknownState(self):
        if self.pinSCK == 1:
            ## rising edge -- read
            self.receiveBit()
            return
        
        ## falling edge -- check state
        ### searching start sequence
        if self.receiveBuffer == 0b10101010:
            self.unknownState = False
            self.edgeCunter = 15
            self.receivedByte()
            self.edgeCunter = 0
            self.receiveBuffer = 0
        else:
            print "unknown state: {0:#010b}".format(self.receiveBuffer)


    def slaveSelected(self):
        self.sendBit()
        
    def slave_tick(self, channel):
        ## Needed to modify global copy of globvar
        global bucket
        
        try:
            pinSS = GPIO.input(PIN_SS)
            if pinSS == 1:
                return
            self.slaveSelected()
        except:
            bucket.put(sys.exc_info())

        
        
## ==================================================================



GPIO.setmode(GPIO.BCM) 	        				            ## broadcom numbering
GPIO.setup(PIN_SCK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	## set inner pull-down resistor
GPIO.setup(PIN_DI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	    ## set inner pull-down resistor
GPIO.setup(PIN_DO, GPIO.OUT )
GPIO.setup(PIN_SS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	    ## set inner pull-down resistor


try:
    spi = SpiSlave()
    
    ## when a changing edge is detected on given port, regardless of whatever   
    ## else is happening in the program, the function my_callback will be run  
    GPIO.add_event_detect(PIN_SCK, GPIO.BOTH, callback=spi.clock_tick)
    GPIO.add_event_detect(PIN_SS, GPIO.BOTH, callback=spi.slave_tick)
    
    
    while True:
        ## handle callback exceptions
        try:
            ##exc = bucket.get(block=False)
            exc = bucket.get(timeout=1000)
        except Queue.Empty:
            ## timeout
            pass
        else:
            #### deal with the exception
            exc_type, exc_obj, exc_trace = exc
            print "\nTraceback (most recent call last):"
            traceback.print_tb(exc_trace)
            print "{}: {}".format(exc_type.__name__, exc_obj )
            exit(1)
            
        
except KeyboardInterrupt:
    ## do nothing
    pass

finally:
    print "Cleaning up"
    GPIO.cleanup()

