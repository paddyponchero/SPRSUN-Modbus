# SPRSUN-Modbus
SPRSUN-Modbus Heat Pump Python Plugin for Domoticz

Forked from simat-git/SDM120-Modbus 

This version allows multiple instances to work on Domoticz 2023.1 which uses multithreaded loading of the Plugins.
Exclusive access on the serial port is now enforced to ensure only one instance at a time can access that port.

Has been tested on a USB to RS485 interface (FTDI FT232R chip) with a couple of Plugin instances accessing a SPRSUN Heat Pump.

Installation: <br>
cd ~/domoticz/plugins<br>
git clone https://github.com/Sateetje/SPRSUN-Modbus<br>

<br>
Used python modules: <br>
pyserial -> -https://pythonhosted.org/pyserial/ <br>
minimalmodbus -> http://minimalmodbus.readthedocs.io<br>
<br>
Restart your domoticz server using - sudo service domoticz.sh restart
<br>
<br>
Tested on domoticz 2021.1 and 2023.1, Python 3.9.2.  MinimalModbus included is 2.0.1

