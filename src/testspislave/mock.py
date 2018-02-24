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

from spislave.pinaccess import PinAccess
from spislave.spidevice import SpiDevice


#
#
#
class SlaveDeviceMock(SpiDevice):
    def __init__(self):
        SpiDevice.__init__(self)
        self.activateCounter = 0
        self.deactivateCounter = 0
        self.loadBitToSendCounter = 0
        self.storeReceivedBitCounter = 0
        self.receiveBuffer = 0
    
    def activate(self):
        self.activateCounter += 1

    def deactivate(self):
        self.deactivateCounter += 1

    def loadBitToSend(self):
        self.loadBitToSendCounter += 1
        return 0

    def storeReceivedBit(self, bit):
        self.storeReceivedBitCounter += 1
        self.receiveBuffer = (self.receiveBuffer << 1) | (bit & 1)
        mask = ((1 << self.storeReceivedBitCounter) - 1)
        self.receiveBuffer = self.receiveBuffer & mask



#
#
#
class PinAccessMock(PinAccess):
    def __init__(self):
        self.diPin = 0
        self.sckCallback = None
        self.ssCallback = None
        self.doBuffer = 0
    
    def readDI(self): 
        return self.diPin

    def writeDO(self, value):
        self.doBuffer = (self.doBuffer << 1) | (value & 1)
    
    def registerForSCK(self, callback): 
        self.sckCallback = callback

    def registerForSS(self, callback): 
        self.ssCallback = callback
    
    ## receive 8bit value
    def sendToSlave(self, value):
        assert self.sckCallback != None
        
        if self.ssCallback != None:
            self.ssPin = 0
            self.ssCallback(0)
        
        dataBuffer = value
        ##print "sending data:", bin(dataBuffer)
        
        for _ in range(0, 8):
            dataBuffer = dataBuffer << 1
            self.diPin = int( ((dataBuffer & 0x100) != 0) )
            ## print "set pin:", self.diPin
            self.sckCallback(1)
            self.sckCallback(0)
        
        if self.ssCallback != None:
            self.ssPin = 1
            self.ssCallback(1)
    
