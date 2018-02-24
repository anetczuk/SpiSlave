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
from spislave.spidevice import SpiAbstractDevice



#
# Middle layer -- transmission protocol
# We assume that transmission is 8bit
#
class SSProtocol(object):
    def __init__(self, dataAccessor = None, spiDevice = None):
        if dataAccessor is None:
            self.dataAccess = PinAccess()
        else:
            self.dataAccess = dataAccessor
            
        if spiDevice is None:
            self.device = SpiAbstractDevice()
        else:
            self.device = spiDevice            
            
        self.dataAccess.registerForSCK( self.clock_tick )
        self.dataAccess.registerForSS( self.slave_tick )
        self.clockCouter = 0
        self.selected = False

    def sendBit(self):
        if self.clockCouter <= 0:
            return
        bit = self.device.loadBitToSend()
        self.dataAccess.writeDO(bit)

    def receiveBit(self):
        bit = self.dataAccess.readDI()
        self.device.storeReceivedBit(bit)

    ## Define a threaded callback function to run in another thread when events are detected  
    def clock_tick(self, pinSCK):
        if self.selected == False:
            return
        ##print "protocol clock_tick", pinSCK, self.clockCouter
        if pinSCK == 0:
            self.sendBit()
        else:
            self.receiveBit()
        self.clockCouter -= 1
        
    def slave_tick(self, pinSS):
        ##print "protocol slave_tick"
        if pinSS == 0:
            self.clockCouter = 15
            self.selected = True
            self.device.activate()
            self.sendBit()
        else:
            self.clockCouter = 0
            self.selected = False
            self.device.deactivate()



##
## Implementation of SPI without SS line.
## It can be useful when connecting only two devices without need of SS.
##
class NoSSProtocol(object):
    def __init__(self, dataAccessor = None, spiDevice = None):
        if dataAccessor is None:
            self.dataAccess = PinAccess()
        else:
            self.dataAccess = dataAccessor
            
        if spiDevice is None:
            self.device = SpiAbstractDevice()
        else:
            self.device = spiDevice            
            
        self.dataAccess.registerForSCK( self.clock_tick )
        self.dataAccess.registerForSS( None )
        self.startSequence = None
        self.sequenceBuffer = 0
        self.receiveCounter = 0

    def waitForSequence(self, sequence):
        self.startSequence = sequence

    def sendBit(self):
        bit = self.device.loadBitToSend()
        self.dataAccess.writeDO(bit)

    def receiveBit(self):
        bit = self.dataAccess.readDI()
        ##print "received bit:", bit
        if self.startSequence == None:
            ## start sequence received
            self.device.storeReceivedBit(bit)
            self.receiveCounter += 1
            if self.receiveCounter >= 8:
                ## next byte
                self.receiveCounter = 0
                self.device.deactivate()
                self.device.activate()
            return
            
        ## checkign start sequence
        self.sequenceBuffer = (self.sequenceBuffer << 1) | (bit & 1)
        if (len( bin(self.sequenceBuffer) )-2) > 8:
            self.sequenceBuffer = self.sequenceBuffer & 0xFF
            
        ## print "sequence buffer:", '{0:08b}'.format(self.sequenceBuffer), '{0:08b}'.format(self.startSequence)
        if self.sequenceBuffer == self.startSequence:
            self.startSequence = None
            self.device.receiveBuffer = self.sequenceBuffer
            self.device.deactivate()
            self.device.activate()
            self.sendBit()
            

    ## Define a threaded callback function to run in another thread when events are detected  
    def clock_tick(self, pinSCK):
        ##print "protocol clock_tick", pinSCK, self.clockCouter
        if pinSCK == 0:
            self.sendBit()
        else:
            self.receiveBit()

