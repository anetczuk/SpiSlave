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


# import sys
# import Queue



#
# Abstract SPI device
#
class SpiAbstractDevice(object):

    def activate(self):
        ## override
        pass

    def deactivate(self):
        ## override
        pass

    def loadBitToSend(self):
        ## override
        return 0

    def storeReceivedBit(self, bit):
        ## override
        pass



#
# SPI device
#
class SpiDevice(SpiAbstractDevice):
    def __init__(self):
        self.receiveBuffer = 0
        self.sendBuffer = 0
        self.loadBitIndex = 0
        
    ## called before start of transmission (slave pin raised)
    def prepareData(self):
        ## override
        pass

    ## called after end of transmission (slave pin release)
    def dataReceived(self):
        ## override
        pass

    def activate(self):
        ##print "spi slaveActivated"
        self.receiveBuffer = 0
        self.loadBitIndex = 7
        self.prepareData()

    def deactivate(self):
        ##print "spi slaveDeactivated"
        self.sendBuffer = 0
        self.dataReceived()

    def loadBitToSend(self):
        ##print "echo received: {0:#010b}".format(self.receiveBuffer)
        bitMask = (1 << self.loadBitIndex)
        value = self.sendBuffer & bitMask
        bit = int( value != 0 )
        ##print "sending bit:", bit, bin(self.sendBuffer), "index:", self.loadBitIndex
        self.loadBitIndex -= 1
        if self.loadBitIndex < 0:
            self.loadBitIndex = 7
            self.sendBuffer = self.sendBuffer >> 8
        return bit

    def storeReceivedBit(self, bit):
        ##print "spi slave received bit:", bit, bin(self.receiveBuffer)
        self.receiveBuffer = (self.receiveBuffer << 1) | (bit & 1)

