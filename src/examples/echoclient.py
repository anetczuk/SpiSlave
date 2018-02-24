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


import argparse

from spislave.spidevice import SpiSlave
from spislave.protocol import SSProtocol
from spislave.protocol import NoSSProtocol
from spislave.rpigpioaccess import RPiGPIOAccess

import Queue
import traceback



#
# Echo client handling master without SS line (slave is always activated).
#
class EchoSlaveNoSS(SpiSlave):
    def __init__(self):
        SpiSlave.__init__(self)
        self.dataAccess = RPiGPIOAccess()
        self.dataAccess.registerForSS(None)
        self.protocol = NoSSProtocol( self.dataAccess, self )
        self.protocol.waitForSequence(0b10101010)

    def prepareData(self):
        ##self.sendBuffer = 55
        print "echo prepareData: {0}[{0:#010b}]".format(self.sendBuffer)

    def dataReceived(self):
        print "echo received: {0}[{0:#010b}]".format(self.receiveBuffer)
        if self.receiveBuffer == 170:
            self.sendBuffer = 55
        else:
            self.sendBuffer = 0

    def run(self):
        self.dataAccess.start()
        while True:
            ## handle callback exceptions
            try:
                ##exc = bucket.get(block=False)
                exc = self.dataAccess.getException(1000)
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



#
# Echo client handling master
#
class EchoSlave(SpiSlave):
    def __init__(self):
        SpiSlave.__init__(self)
        self.dataAccess = RPiGPIOAccess()
        self.protocol = SSProtocol( self.dataAccess, self )
        self.counter = 0

    def prepareData(self):
        self.counter += 1
        self.sendBuffer = self.counter
        print "echo prepareData: {0}[{0:#010b}]".format(self.sendBuffer)

    def dataReceived(self):
        print "echo received: {0}[{0:#010b}]".format(self.receiveBuffer)

    def run(self):
        self.dataAccess.start()
        while True:
            ## handle callback exceptions
            try:
                ##exc = bucket.get(block=False)
                exc = self.dataAccess.getException(1000)
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



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Echo slave client example')
    parser.add_argument('--noss', action='store_const', const=True, default=False, help='No SS echo version - always activated' )
    
    args = parser.parse_args()
    
    try:
        print "Waiting for master"
        
        echo = None
        if args.noss:
            echo = EchoSlaveNoSS()
        else:
            echo = EchoSlave()
        
        echo.run()
        
    except KeyboardInterrupt:
        ## do nothing
        pass

    finally:
        print "Cleaning up"
        RPiGPIOAccess.cleanup()

