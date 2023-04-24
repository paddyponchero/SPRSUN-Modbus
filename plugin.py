#!/usr/bin/env python
"""
Eastron SDM120-Modbus Smart Meter Single Phase Electrical System. The Python plugin for Domoticz
Original Author: MFxMF and bbossink and remcovanvugt
Better Error handling and event recovery added by simat-git 2023.

Works with Eastron SDM120M / SDM120CT-M, can be easily adapted to any Modbus meter.

Requirements: 
    1.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    2.Communication module Modbus USB to RS485 converter module
"""
"""
<plugin key="SDM120M" name="SDM120-Modbus" version="2" author="simat-git">
    <params>
        <param field="SerialPort" label="Modbus Port" width="200px" required="true" default="/dev/ttyUSB0" />
        <param field="Mode1" label="Baud rate" width="40px" required="true" default="9600"  />
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
        Domoticz.Log("SDM120M Modbus plugin start")
        self.runInterval = int(Parameters["Mode3"]) * 1 
        
        if 1 not in Devices:
            Domoticz.Device(Name="Total System Power", Unit=1,TypeName="Usage",Used=0).Create()
        Options = { "Custom" : "1;VA"} 
        if 2 not in Devices:
            Domoticz.Device(Name="Import Wh", Unit=2,Type=243,Subtype=29,Used=0).Create()
        Options = { "Custom" : "1;kVArh"}
        if 3 not in Devices:
            Domoticz.Device(Name="Export Wh", Unit=3,Type=243,Subtype=29,Used=0).Create()
        Options = { "Custom" : "1;kVArh"} 
        if 4 not in Devices:
            Domoticz.Device(Name="Total kWh", Unit=4,Type=243,Subtype=29,Used=0).Create()
        Options = { "Custom" : "1;kVArh"}
        if 5 not in Devices:
            Domoticz.Device(Name="Voltage", Unit=5,Type=243,Subtype=8,Used=0).Create()
        Options = { "Custom" : "1;V"}
        if 6 not in Devices:
            Domoticz.Device(Name="Import power", Unit=6,TypeName="Usage",Used=0).Create()
        Options = { "Custom" : "1;VA"} 
        if 7 not in Devices:
            Domoticz.Device(Name="Export power", Unit=7,TypeName="Usage",Used=0).Create()
        Options = { "Custom" : "1;VA"} 

    def onStop(self):
        Domoticz.Log("SDM120M Modbus plugin stop")

    def onHeartbeat(self):
        self.runInterval -=1;
        if self.runInterval <= 0:
        
            Total_System_Power = 0  #  Declare these to keep the debug section at the bottom from complaining.
            Import_Wh = 0
            Export_Wh = 0
            Total_kwh = 0
            Voltage = 0
            Import_power = 0
            Export_power = 0
            
            # Get data from SDM120M
            try:
                 self.rs485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(Parameters["Mode2"]))
                 #class minimalmodbus.Instrument(port: str, slaveaddress: int, mode: str = 'rtu', close_port_after_each_call: bool = False, debug: bool = False)
                 self.rs485.serial.baudrate = Parameters["Mode1"]
                 self.rs485.serial.bytesize = 8
                 self.rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
                 self.rs485.serial.stopbits = 1
                 self.rs485.serial.timeout = 1
                 self.rs485.serial.exclusive = True # From Forum
                 self.rs485.debug = False
                            
                 self.rs485.mode = minimalmodbus.MODE_RTU
                 self.rs485.close_port_after_each_call = True
                 
                 Total_System_Power = self.rs485.read_float(12, 4, 2)
                 Import_Wh = self.rs485.read_float(72, 4, 2)
                 Export_Wh = self.rs485.read_float(74, 4, 2)
                 Total_kwh = self.rs485.read_float(342, 4, 2)
                 Voltage = self.rs485.read_float(0, 4, 2)
                 Import_power = self.rs485.read_float(88, 4, 2)
                 Export_power = self.rs485.read_float(92, 4, 2)
                 #self.rs485.read_float(register, functioncode, numberOfRegisters)
                 self.rs485.serial.close()  #  Close that door ! // does this even work !! ??
            except:
                Domoticz.Heartbeat(1)   # set Heartbeat to 1 second to get us back here for quick retry.
                self.runInterval = 1    # call again in 10 seconds
                Domoticz.Log("**** SDM120M Connection problem ****");
            else:
                #Update devices
                Devices[1].Update(0,str(Total_System_Power))
                Devices[2].Update(0,str(Total_System_Power)+";"+str(Import_Wh*1000))
                Devices[3].Update(0,str(Export_Wh))
                Devices[4].Update(0,str(Total_kwh))
                Devices[5].Update(0,str(Voltage))
                Devices[6].Update(0,str(Import_power))
                Devices[7].Update(0,str(Export_power))
                self.runInterval = int(Parameters["Mode3"]) * 6 # Success so call again in 60 seconds.
                Domoticz.Heartbeat(10)  # Sucesss so set Heartbeat to 10 second intervals.


            if Parameters["Mode6"] == 'Debug':
                Domoticz.Log("SDM120M Modbus Data")
                Domoticz.Log('Total system power: {0:.3f} W'.format(Total_System_Power))
                Domoticz.Log('Import Wh: {0:.3f} kWh'.format(Import_Wh))
                Domoticz.Log('Export Wh: {0:.3f} kWh'.format(Export_Wh))
                Domoticz.Log('Total kwh: {0:.3f} kWh'.format(Total_kwh))
                Domoticz.Log('Voltage: {0:.3f} V'.format(Voltage))
                Domoticz.Log('Import power: {0:.3f} W'.format(Import_power))
                Domoticz.Log('Export power: {0:.3f} W'.format(Export_power))

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
