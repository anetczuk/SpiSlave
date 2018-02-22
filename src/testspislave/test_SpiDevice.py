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


import unittest

from spislave.SpiDevice import SpiSlave
from spislave.SpiDevice import SpiDevice
from spislave.Protocol import SSProtocol
from spislave.Protocol import NoSSProtocol
from spislave.PinAccess import PinAccess
 
 
#__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



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
    
    def __del__(self): pass
        
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
        PinAccess.__init__(self)
        self.diPin = 0
        self.sckCallback = None
        self.ssCallback = None
        self.doBuffer = 0
    
    def __del__(self): pass
        
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



#
#
#
class SpiSlaveTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_default(self):
        slave = SpiSlave()
        self.assertEqual( slave.receiveBuffer, 0 )
        self.assertEqual( slave.sendBuffer, 0 )
        self.assertEqual( slave.loadBitIndex, 0 )

    def test_activate(self):
        slave = SpiSlave()
        slave.activate()
        self.assertEqual( slave.receiveBuffer, 0 )
        self.assertEqual( slave.loadBitIndex, 7 )
        
    def test_loadBitToSend(self):
        slave = SpiSlave()
        slave.activate()
        
        slave.sendBuffer = 0b10100000
        
        self.assertEqual( slave.loadBitToSend(), 1 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitToSend(), 1 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitIndex, 2 )

        
    def test_storeReceivedBit(self):
        slave = SpiSlave()
        self.assertEqual( slave.receiveBuffer, 0 )
        self.assertEqual( slave.sendBuffer, 0 )
        self.assertEqual( slave.loadBitIndex, 0 )
        



#
#
#
class SSProtocolTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self.dataAccess = PinAccessMock()
        self.device = SlaveDeviceMock()
        self.protocol = SSProtocol( self.dataAccess, self.device )
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_sendBit(self):
        self.protocol.clockCouter = 1
        self.protocol.sendBit()
        self.assertEqual( self.device.loadBitToSendCounter, 1 )

    def test_sendBit_noClock(self):
        self.protocol.sendBit()
        self.assertEqual( self.device.loadBitToSendCounter, 0 )

    def test_clock_tick_notselected(self):
        self.protocol.clock_tick(1)
        self.assertEqual( self.protocol.clockCouter, 0 )

    def test_clock_tick_low(self):
        self.protocol.selected = True
        self.protocol.clockCouter = 4
        self.protocol.clock_tick(0)
        self.assertEqual( self.device.loadBitToSendCounter, 1 )
        self.assertEqual( self.protocol.clockCouter, 3 )

    def test_clock_tick_high(self):
        self.protocol.selected = True
        self.protocol.clock_tick(1)
        self.assertEqual( self.device.storeReceivedBitCounter, 1 )
        self.assertEqual( self.protocol.clockCouter, -1 )

    def test_slave_tick_activated(self):
        self.protocol.slave_tick(0)
        self.assertEqual( self.protocol.clockCouter, 15 )
        self.assertEqual( self.protocol.selected, True )
        self.assertEqual( self.device.activateCounter, 1 )
        self.assertEqual( self.device.loadBitToSendCounter, 1 )

    def test_slave_tick_deactivated(self):
        self.protocol.slave_tick(1)
        self.assertEqual( self.protocol.clockCouter, 0 )
        self.assertEqual( self.protocol.selected, False )
        self.assertEqual( self.device.deactivateCounter, 1 )
        
    def test_receiveByte(self):
        self.dataAccess.sendToSlave(0xCC)
        self.assertEqual( self.protocol.clockCouter, 0 )
        self.assertEqual( self.protocol.selected, False )
        self.assertEqual( self.device.receiveBuffer, 0xCC )
        
        

#
#
#
class NoSSProtocolTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self.dataAccess = PinAccessMock()
        self.device = SlaveDeviceMock()
        self.protocol = NoSSProtocol( self.dataAccess, self.device )
        pass
 
    def tearDown(self):
        # Called after the last testfunction was executed
        pass

    def test_clock_tick_low(self):
        self.protocol.clock_tick(0)
        self.assertEqual( self.device.loadBitToSendCounter, 1 )

    def test_clock_tick_high(self):
        self.protocol.clock_tick(1)
        self.assertEqual( self.device.storeReceivedBitCounter, 1 )

    def test_transmission_start(self):
        self.protocol.waitForSequence(0b11000111)
        
        self.dataAccess.sendToSlave(0b11000111)
        self.assertEqual( self.device.storeReceivedBitCounter, 0 )
        self.assertEqual( self.device.receiveBuffer, 0b11000111 )
        self.assertEqual( self.device.activateCounter, 1 )
        self.assertEqual( self.device.deactivateCounter, 1 )
        
        self.dataAccess.sendToSlave(0b10010101)
        self.assertEqual( self.device.storeReceivedBitCounter, 8 )
        self.assertEqual( self.device.receiveBuffer, 0b10010101 )
        self.assertEqual( self.device.activateCounter, 2 )
        self.assertEqual( self.device.deactivateCounter, 2 )


    def test_transmission_startlong(self):
        self.protocol.waitForSequence(0b11000111)
        
        self.dataAccess.sendToSlave(0b10101010)
        self.dataAccess.sendToSlave(0b11000111)
        self.assertEqual( self.device.activateCounter, 1 )
        self.assertEqual( self.device.deactivateCounter, 1 )


#
#
#
class TransmissionTest(unittest.TestCase):
    def setUp(self):
        # Called before the first testfunction is executed
        self.dataAccess = PinAccessMock()
        self.device = SpiSlave()
        self.protocol = SSProtocol( self.dataAccess, self.device )
        pass
        
    def test_transmission_1(self):        
        self.device.sendBuffer = 1
        self.dataAccess.sendToSlave(128)                   # 0b10000000
        
        self.assertEqual( self.device.receiveBuffer, 128 )
        self.assertEqual( self.device.sendBuffer, 0 )
        self.assertEqual( self.dataAccess.doBuffer, 1 )

    def test_transmission_22(self):
        self.device.sendBuffer = 22
        self.dataAccess.sendToSlave(66)
        
        self.assertEqual( self.device.receiveBuffer, 66 )
        self.assertEqual( self.device.sendBuffer, 0 )
        self.assertEqual( self.dataAccess.doBuffer, 22 )      ## 22 = 0b00010110



if __name__ == "__main__":
    unittest.main()
