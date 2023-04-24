# SDM120-Modbus
Eastron SDM120-Modbus RTU Single Phase kWh Meter

Forked from MFxMF/SDM630-Modbus

This version allow multiple instances to work on Domoticz 2023.1 which uses multithreaded loading of the Plugins.
Exclusive access on the serial port is now enforced to ensure only one instance at a time can access that port.

Has been tested on a USB to RS485 interface (FTDI FT232R chip) with 20 Plugin instances accessing several SDM120M and SDM120M-CT meters.

Installation: <br>
cd ~/domoticz/plugins<br>
git clone https://github.com/simat-git/SDM120-Modbus <br>

<br>
Used python modules: <br>
pyserial -> -https://pythonhosted.org/pyserial/ <br>
minimalmodbus -> http://minimalmodbus.readthedocs.io<br>
<br>
Restart your domoticz server using - sudo service domoticz.sh restart
<br>
<br>
Tested on domoticz 2021.1 ane 2023.1

