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

from spislave.spidevice import SpiSlave
 
 
#__scriptdir__ = os.path.dirname(os.path.realpath(__file__))
# logging.basicConfig(level=logging.INFO)



#
#
#
class SpiSlaveTest(unittest.TestCase):
    def setUp(self):
        # Called before execution of each testfunction
        pass
 
    def tearDown(self):
        # Called after execution of each testfunction
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
        
    def test_deactivate(self):
        slave = SpiSlave()
        slave.sendBuffer = 12
        slave.deactivate()
        self.assertEqual( slave.sendBuffer, 0 )
        
    def test_loadBitToSend(self):
        slave = SpiSlave()
        slave.activate()
        
        inputBuffer = 0b10100000
        slave.sendBuffer = inputBuffer
        
        self.assertEqual( slave.loadBitToSend(), 1 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitToSend(), 1 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitIndex, 2 )
        
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitIndex, 0 )
        self.assertEqual( slave.sendBuffer, inputBuffer )
        
        self.assertEqual( slave.loadBitToSend(), 0 )
        self.assertEqual( slave.loadBitIndex, 7 )
        self.assertEqual( slave.sendBuffer, 0 )

    def test_storeReceivedBit(self):
        slave = SpiSlave()
        self.assertEqual( slave.receiveBuffer, 0 )
        self.assertEqual( slave.sendBuffer, 0 )
        self.assertEqual( slave.loadBitIndex, 0 )
        
        slave.storeReceivedBit(1)
        self.assertEqual( slave.receiveBuffer, 1 )
        self.assertEqual( slave.sendBuffer, 0 )
        self.assertEqual( slave.loadBitIndex, 0 )



if __name__ == "__main__":
    unittest.main()
