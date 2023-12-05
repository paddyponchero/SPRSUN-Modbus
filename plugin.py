#!/usr/bin/env python
"""
SPRSUN-Modbus Heat Pump. The Python plugin for Domoticz
Original Author: MFxMF and bbossink and remcovanvugt
Better Error handling and event recovery added by simat-git 2023.
Converted from Eastron SDM120M to SPRSUN plugin by Sateetje 2023.

Works with SPRSUN HeatPump CGK0x0V2.

Requirements: 
    1.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    2.Communication module Modbus USB to RS485 converter module
"""
"""
<plugin key="SPRSUN" name="SPRSUN-Modbus" version="1" author="Sateetje">
    <params>
        <param field="SerialPort" label="Modbus Port" width="200px" required="true" default="/dev/ttyUSB0" />
        <param field="Mode1" label="Baud rate" width="40px" required="true" default="19200"  />
        <param field="Mode2" label="Device ID" width="40px" required="true" default="1" />
        <param field="Mode3" label="Reading Interval min." width="40px" required="true" default="1" />
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>

"""

import minimalmodbus    #v2.0.1
#import serial          #minimalmodbus imports this now.
import Domoticz         #tested on Python 3.9.2 in Domoticz 2021.1 and 2023.1


class BasePlugin:
    def __init__(self):
        self.runInterval = 1
        self.rs485 = "" 
        return

    def onStart(self):
        
        devicecreated = []
        Domoticz.Log("SPRSUN-Modbus plugin start")
        self.runInterval = int(Parameters["Mode3"]) * 1 
        
        if 1 not in Devices:
            Domoticz.Device(Name="Hot water temperature", Unit=1,TypeName="Temp",Subtype="LaCrosse TX3",Used=0).Create()
            Options = { "Custom" : "1;C"} 

    def onStop(self):
        Domoticz.Log("SPRSUN-Modbus plugin stop")

    def onHeartbeat(self):
        self.runInterval -=1;
        if self.runInterval <= 0:
        
            Hot_Water_Temperature = 0  #  Declare these to keep the debug section at the bottom from complaining.
            
            # Get data from SPRSUB
            try:
                 self.rs485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(Parameters["Mode2"]))
                 #class minimalmodbus.Instrument(port: str, slaveaddress: int, mode: str = 'rtu', close_port_after_each_call: bool = False, debug: bool = False)
                 self.rs485.serial.baudrate = Parameters["Mode1"]
                 self.rs485.serial.bytesize = 8
                 self.rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
                 self.rs485.serial.stopbits = 1
                 self.rs485.serial.timeout = 1
                 self.rs485.serial.exclusive = True # Fix From Forum Member 'lost'
                 self.rs485.debug = False
                            
                 self.rs485.mode = minimalmodbus.MODE_RTU
                 self.rs485.close_port_after_each_call = True
                 
                 Hot_Water_Temperature = self.rs485.read_float(195, 4, 1)
                 #self.rs485.read_float(register, functioncode, numberOfRegisters)
                 self.rs485.serial.close()  #  Close that door !
            except:
                Domoticz.Heartbeat(1)   # set Heartbeat to 1 second to get us back here for quick retry.
                self.runInterval = 1    # call again in 1 second
                Domoticz.Log("**** SPRSUN Connection problem ****");
            else:
                #Update devices
                Devices[1].Update(0,str(Hot_Water_Temperature))
                self.runInterval = int(Parameters["Mode3"]) * 6 # Success so call again in 60 seconds.
                Domoticz.Heartbeat(10)  # Sucesss so set Heartbeat to 10 second intervals.


            if Parameters["Mode6"] == 'Debug':
                Domoticz.Log("SPRSUN Modbus Data")
                Domoticz.Log('Hot water temperature: {0:.1f} C'.format(Hot_Water_Temperature))

            #self.runInterval = int(Parameters["Mode3"]) * 6

global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
            Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
