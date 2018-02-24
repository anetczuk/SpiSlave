## SpiSlave

Implementation of slave mode of SPI bus for Raspberry Pi.  
Library can be used for example to mock slave node during implementation or testing of master node.


### Requirements

* Python 2.7
* Raspberry Pi with RPi.GPIO module


### Limitations

* transmission of 8-bit words only,
* no driver support, so high frequencies can be an issue



### Details

This is software implementation of SPI bus. As hardware layer it uses Raspberry Pi's GPIO pins.

Module is prepared to operate in two modes: supporting and without _SS_ line. _NoSS_ mode is useful in case when there is only one slave, so _SS_ pin can be used for other purpose.

Unit tests can be run by _test_runner.py_ script. No _GPIO_ module needed.

#### Classes

* __pinaccess.PinAccess__ - dummy accessor to wires,
* __rpigpioaccess.RPiGPIOAccess__ - accessor to RPi's GPIO pins,
* __spidevice.SpiAbstractDevice__ - abstract representation of device,
* __spidevice.SpiDevice__ - implementation of transmitter,
* __protocol.SSProtocol__ - implementation of SPI 8-bit word transmission prototcol,
* __protocol.NoSSProtocol__ - alternative 8-bit word transmission prototcol without use of SS line


### Examples

* examples.echoclient - simple client receiving data from master and sending number sequences,
* examples.gpio - another implementation of client sending sequence of numbers


### References

* https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus - description of SPI bus,
* [Python Spidev](https://pypi.python.org/pypi/spidev) - _Python bindings for Linux SPI access through spidev_, **master mode only**
