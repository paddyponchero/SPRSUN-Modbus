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
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>

"""

import minimalmodbus    #v2.1.1
import Domoticz         #tested on Python 3.9.2 in Domoticz 2021.1 and 2023.1


class BasePlugin:
    def __init__(self):
        self.runInterval = 1
        self.rs485 = ""
        return

    def onStart(self):
        devicecreated = []
        Domoticz.Log("SPRSUN-Modbus plugin start")
        self.runInterval = 1

        #https://github.com/domoticz/domoticz/blob/master/hardware/hardwaretypes.h
        if 1 not in Devices:
            Domoticz.Device(Name="Return water temperature",Unit=1,Type=80,Subtype=5,Used=1).Create()
        if 2 not in Devices:
            Domoticz.Device(Name="Outlet temperature",Unit=2,Type=80,Subtype=5,Used=1).Create()
        if 3 not in Devices:
            Domoticz.Device(Name="Ambient temperature",Unit=3,Type=80,Subtype=5,Used=1).Create()
        if 4 not in Devices:
            Domoticz.Device(Name="Hot water temperature",Unit=4,Type=80,Subtype=5,Used=1).Create()
        if 5 not in Devices:
            Domoticz.Device(Name="Unit on",Unit=5,Type=244,Subtype=73,Switchtype=0,Image=9,Used=1).Create()
        if 6 not in Devices:
            Domoticz.Device(Name="Fan output",Unit=6,Type=243,Subtype=6,Used=1).Create()
        if 7 not in Devices:
            Domoticz.Device(Name="Pump output",Unit=7,Type=243,Subtype=6,Used=1).Create()
        if 8 not in Devices:
            Domoticz.Device(Name="Required cap",Unit=8,Type=243,Subtype=6,Used=1).Create()
        if 9 not in Devices:
            Domoticz.Device(Name="Actual cap",Unit=9,Type=243,Subtype=6,Used=1).Create()
        if 10 not in Devices:
            Domoticz.Device(Name="Power",Unit=10,Type=248,Subtype=1,Used=1).Create()
        if 11 not in Devices:
            Domoticz.Device(Name="Voltage",Unit=11,Type=243,Subtype=8,Used=1).Create()
        if 12 not in Devices:
            Domoticz.Device(Name="Current",Unit=12,Type=243,Subtype=23,Used=1).Create()
        if 13 not in Devices:
            Domoticz.Device(Name="Setpoint Hot Water",Unit=13,Type=242,Subtype=1,Used=1).Create()
        if 14 not in Devices:
            Domoticz.Device(Name="Setpoint Heating",Unit=14,Type=242,Subtype=1,Used=1).Create()
        Options = {"LevelActions": "|| ||", "LevelNames": "Off|Cooling|Heating|Hot Water|Hot Water + Cooling|Hot Water + Heating", "LevelOffHidden": "true", "SelectorStyle": "1"}
        if 15 not in Devices:
            Domoticz.Device(Name="Mode",Unit=15,TypeName="Selector Switch",Options=Options,Image=15,Used=1).Create()
        if 16 not in Devices:
            Domoticz.Device(Name="Status",Unit=16,Type=243,Subtype=19,Used=1).Create()
        if 17 not in Devices:
            Domoticz.Device(Name="Three-way valve",Unit=17,Type=244,Subtype=73,Switchtype=0,Used=1).Create()
        if 18 not in Devices:
            Domoticz.Device(Name="Heater",Unit=18,Type=244,Subtype=73,Switchtype=0,Image=15,Used=1).Create()
        if 19 not in Devices:
            Domoticz.Device(Name="Linkage",Unit=19,Type=244,Subtype=73,Switchtype=2,Used=1).Create()

    def onStop(self):
        Domoticz.Log("SPRSUN-Modbus plugin stop")

    def onHeartbeat(self):
        self.runInterval -=1;
        if self.runInterval <= 0:

            PV_Return_Water_Temperature = 0 #  Declare these to keep the debug section at the bottom from complaining.
            PV_Outlet_Temperature = 0
            PV_Ambient_Temperature = 0
            PV_Hot_Water_Temperature = 0
            Unit_On = 0
            PV_Fan_Output = 0
            PV_Pump_Output = 0
            PV_Required_Cap = 0
            PV_Actual_Cap = 0
            PV_Power = 0
            PV_Voltage = 0
            PV_Current = 0
            SP_Hot_Water = 0
            SP_Heating = 0
            Mode = 0
            Status = 0
            StatusText = "Unknown"
            ThreeWayValve = 0
            Heater = 0
            Linkage = 0

            # Get data from SPRSUN
            try:
                 self.rs485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(Parameters["Mode2"]))
                 self.rs485.serial.baudrate = Parameters["Mode1"]
                 self.rs485.serial.bytesize = 8
                 self.rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
                 self.rs485.serial.stopbits = 1
                 self.rs485.serial.timeout = 1
                 self.rs485.serial.exclusive = True # Fix From Forum Member 'lost'
                 self.rs485.debug = False
                 self.rs485.mode = minimalmodbus.MODE_RTU
                 self.rs485.close_port_after_each_call = True

                 PV_Return_Water_Temperature = self.rs485.read_register(188,1,3,False)
                 PV_Outlet_Temperature = self.rs485.read_register(189,1,3,False)
                 PV_Ambient_Temperature = self.rs485.read_register(190,1,3,False)
                 PV_Hot_Water_Temperature = self.rs485.read_register(195,1,3,False)
                 Unit_On = self.rs485.read_bit(40, 1)
                 PV_Fan_Output = self.rs485.read_register(197,1,3,False)
                 PV_Pump_Output = self.rs485.read_register(198,1,3,False)
                 PV_Required_Cap = self.rs485.read_register(203,1,3,False)
                 PV_Actual_Cap = self.rs485.read_register(204,1,3,False)
                 PV_Power = self.rs485.read_register(333,1,3,False)   #Strange value
                 PV_Voltage = self.rs485.read_register(334,0,3,False) #Strange value
                 PV_Current = self.rs485.read_register(335,1,3,False)
                 SP_Hot_Water = self.rs485.read_register(3,1,3,False)
                 SP_Heating = self.rs485.read_register(1,1,3,False)
                 Mode = self.rs485.read_register(0,0,3,False)
                 Status = self.rs485.read_register(217,0,3,False)
                 ThreeWayValve = self.rs485.read_bit(11, 2)
                 Heater = self.rs485.read_bit(12, 2)
                 Linkage = self.rs485.read_bit(3, 2)

                 #Convert State to Text
                 if Status == 0:
                      StatusText = "Unit not Ready"
                 elif Status == 1:
                      StatusText = "Unit ON"
                 elif Status == 2:
                      StatusText = "OFF by Alarm"
                 elif Status == 3:
                      StatusText = "OFF by Timezone"
                 elif Status == 4:
                      StatusText = "OFF by SuperV"
                 elif Status == 5:
                      StatusText = "OFF by Linkage"
                 elif Status == 6:
                      StatusText = "OFF by Keyboad"
                 elif Status == 7:
                      StatusText = "Manual Mode"
                 elif Status == 8:
                      StatusText = "Anti Freeze"
                 elif Status == 9:
                      StatusText = "OFF by AC Linkage"
                 elif Status == 10:
                      StatusText = "OFF by Change"
                 else:
                      StatusText == "Unknown"

                 self.rs485.serial.close()  #  Close that door !
            except:
                Domoticz.Heartbeat(1)   # set Heartbeat to 1 second to get us back here for quick retry.
                self.runInterval = 1    # call again in 1 second
                Domoticz.Log("**** SPRSUN Connection problem ****");
            else:
                #Update devices
                Devices[1].Update(0,str(PV_Return_Water_Temperature))
                Devices[2].Update(0,str(PV_Outlet_Temperature))
                Devices[3].Update(0,str(PV_Ambient_Temperature))
                Devices[4].Update(0,str(PV_Hot_Water_Temperature))
                Devices[5].Update(Unit_On,"")
                Devices[6].Update(0,str(PV_Fan_Output))
                Devices[7].Update(0,str(PV_Pump_Output))
                Devices[8].Update(0,str(PV_Required_Cap))
                Devices[9].Update(0,str(PV_Actual_Cap))
                Devices[10].Update(0,str(PV_Power))
                Devices[11].Update(0,str(PV_Voltage))
                Devices[12].Update(0,str(PV_Current))
                Devices[13].Update(nValue=int(SP_Hot_Water),sValue=str(SP_Hot_Water))
                Devices[14].Update(nValue=int(SP_Heating),sValue=str(SP_Heating))
                Devices[15].Update(nValue=int((Mode+1)*10),sValue=str((Mode+1)*10))
                Devices[16].Update(0,StatusText)
                Devices[17].Update(ThreeWayValve,"")
                Devices[18].Update(Heater,"")
                Devices[19].Update(Linkage,"")

                self.runInterval = 1    # Success so call again in 1x10 seconds.
                Domoticz.Heartbeat(10)  # Sucesss so set Heartbeat to 10 second intervals.

            if Parameters["Mode6"] == 'Debug':
                Domoticz.Log("SPRSUN Modbus Data")
                Domoticz.Log('Return water temperature: {0:.1f} C'.format(PV_Return_Water_Temperature))
                Domoticz.Log('Outlet temperature: {0:.1f} C'.format(PV_Outlet_Temperature))
                Domoticz.Log('Ambient temperature: {0:.1f} C'.format(PV_Ambient_Temperature))
                Domoticz.Log('Hot water temperature: {0:.1f} C'.format(PV_Hot_Water_Temperature))
                Domoticz.Log('Unit on: {0}'.format(Unit_On))
                Domoticz.Log('Fan output: {0:.1f}'.format(PV_Fan_Output))
                Domoticz.Log('Pump output: {0:.1f}'.format(PV_Pump_Output))
                Domoticz.Log('Required cap: {0:.1f}'.format(PV_Required_Cap))
                Domoticz.Log('Actual cap: {0:.1f}'.format(PV_Actual_Cap))
                Domoticz.Log('Power: {0:.1f}'.format(PV_Power))
                Domoticz.Log('Voltage: {0}'.format(PV_Voltage))
                Domoticz.Log('Current: {0:.1f}'.format(PV_Current))
                Domoticz.Log('Hot water setpoint: {0:.1f}'.format(SP_Hot_Water))
                Domoticz.Log('Heating setpoint: {0:.1f}'.format(SP_Heating))
                Domoticz.Log('Mode: {0}'.format(Mode))
                Domoticz.Log('Status: ' + StatusText)
                Domoticz.Log('Three-way valve: {0}'.format(ThreeWayValve))
                Domoticz.Log('Heater: {0}'.format(Heater))
                Domoticz.Log('Linkage: {0}'.format(Linkage))

    def onCommand(self, Unit, Command, Level, Hue):
            Domoticz.Log("Something changed for " + Devices[Unit].Name + ", DeviceID = " + str(Unit) + ". New setpoint: " + str(Level) + ". New Command: " + Command)

            sValue=str(Level)
            nValue=int(Level)

            if Unit == 13:
                 #Hot water setpoint
                 nValue=float(Level)
                 self.WriteRS485(3,float(Level),1,False)
            elif Unit == 14:
                 #Heating setpoint
                 nValue=float(Level)
                 self.WriteRS485(1,float(Level),1,False)
            elif Unit == 15:
                 #Mode, when switching mode, need to turn the unit off and on again
                 if Devices[5].nValue == 1:
                      self.WriteRS485(40,0,0,True)

                 self.WriteRS485(0,int((Level/10)-1),0,False)

                 #if Unit was on, turn back on
                 if Devices[5].nValue == 1:
                      self.WriteRS485(40,1,0,True)
            elif Unit == 5:
                 #Unit On
                 if Command == "On":
                     nValue=1
                 else:
                     nValue=0
                 sValue=Command

                 self.WriteRS485(40,nValue,0,True)

            Devices[Unit].Update(nValue=nValue, sValue=sValue)
            Devices[Unit].Refresh()

    def WriteRS485(self, Register, Value, DecimalPlaces, IsBit):
            try:
                 if IsBit == True:
                     self.rs485.write_bit(Register,Value,5) # Value 0 or 1
                 else:
                     self.rs485.write_register(Register,Value,DecimalPlaces,6,False)

                 self.rs485.serial.close()
            except:
                Domoticz.Log("**** SPRSUN Connection problem when writing ****");

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

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

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
