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

import sys, Queue

try:
    import RPi.GPIO as GPIO
except ImportError:
    ##print "Error: RPi.GPIO module not installed, try 'sudo aptitude install python-rpi.gpio' or 'sudo aptitude install python3-rpi.gpio'\n"
    raise



PIN_SCK=11      ## SCLK-GPIO.11 (pin23)
PIN_DI=9        ## MISO-GPIO.9  (pin21)
PIN_DO=10       ## M0SI-GPIO.10 (pin19)
PIN_SS=27       ## GPIO.2       (pin13)


GPIO.setmode(GPIO.BCM) 	        				            ## broadcom numbering
GPIO.setup(PIN_SCK, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	## set inner pull-down resistor
GPIO.setup(PIN_DI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	    ## set inner pull-down resistor
GPIO.setup(PIN_DO, GPIO.OUT )
GPIO.setup(PIN_SS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	    ## set inner pull-down resistor



#
#
#
class RPiGPIOAccess(PinAccess):
    def __init__(self):
        self.sckCallback = None
        self.ssCallback = None
        self.exceptionQueue = Queue.Queue()
        GPIO.add_event_detect(PIN_SCK, GPIO.BOTH, callback=self.clock_tick)
        GPIO.add_event_detect(PIN_SS, GPIO.BOTH, callback=self.slave_tick)
        self.enabled = False

    def start(self): 
        self.enabled = True
    
    def readDI(self): 
        try:
            return GPIO.input(PIN_DI)
        except:
            self.exceptionQueue.put(sys.exc_info())

    def writeDO(self, value): 
        return GPIO.output(PIN_DO, value)

    def registerForSCK(self, callback):
        self.sckCallback = callback

    def registerForSS(self, callback): 
        self.ssCallback = callback
        

    ### ================================================================
    
    def getException(self, accessTimeout=1000):
        return self.exceptionQueue.get( timeout=accessTimeout )

    def clock_tick(self, channel):
        if not (self.enabled is True):
            return
        ##print "RPi GPIO clock_tick:", self.sckCallback
        if self.sckCallback is None:
            return
        pinSCK = self.readSCK()
        self.sckCallback(pinSCK)

    def slave_tick(self, channel):
        if not (self.enabled is True):
            return
        if self.ssCallback is None:
            return
        pinSS = self.readSS()
        ##print "RPi GPIO slave_tick: ", pinSS
        self.ssCallback(pinSS)
        
        
    def readSCK(self):
        try:
            return GPIO.input(PIN_SCK)
        except:
            self.exceptionQueue.put(sys.exc_info())
            
    def readSS(self): 
        try:
            return GPIO.input(PIN_SS)
        except:
            self.exceptionQueue.put(sys.exc_info())

    
    @classmethod
    def cleanup(cls):
        GPIO.cleanup()
    
    
