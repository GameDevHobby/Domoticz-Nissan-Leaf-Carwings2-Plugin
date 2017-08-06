# Carwings Plugin for retrieving battery status (and other info) from a Nissan Leaf
#
# Author: Chris Gheen @GameDevHobby
#
"""
<plugin key="Carwings" name="Carwings (Nissan Leaf)" author="Chris Gheen @GameDevHobby" version="0.5.0" wikilink="" externallink="https://www.nissanusa.com/connect">
    <params>
        <param field="Username" label="Username" width="200px" required="true" default="user"/>
        <param field="Password" label="Password" width="200px" required="true" default="password"/>
        <param field="Mode1" label="Region" width="75px">
            <options>
                <option label="USA" value="NNA"/>
                <option label="Europe" value="NE"/>
                <option label="Canada" value="NCI"/>
                <option label="Australia" value="NMA"/>
                <option label="Japan" value="NML"/>
            </options>
        </param>
        <param field="Mode5" label="Update interval (sec)" width="30px" required="true" default="30"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import subprocess

class BasePlugin:
    enabled = False
    def __init__(self):
        self.debug = False
        return

    def run(self):
        username = Parameters["Username"]
        password = Parameters["Password"]
        region = Parameters["Mode1"]
        cmd = "python " + Parameters["HomeFolder"] + "car.py -u " + username + " -p " + password + " -r " + region 
        #Domoticz.Debug(cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        out = out.decode("utf-8")
        err = err.decode("utf-8")
        
        #Domoticz.Debug(str(p.returncode))
        #Domoticz.Debug(out)
        #Domoticz.Debug(err)
        #self.debug = False

        if p.returncode == 1:
            return str(err)
        else:
            return str(out)


    def onStart(self):
        Domoticz.Log("onStart called")

        if Parameters["Mode6"] == "Debug": 
            self.debug = True
            Domoticz.Debugging(1)
        
        if (len(Devices) == 0):
            Domoticz.Device(Name="Battery", Unit=1, TypeName="Percentage", Used=1).Create()
            Domoticz.Device(Name="Plug Status", Unit=2, TypeName="Text", Used=1).Create()
            Domoticz.Device(Name="Charge Status", Unit=3, TypeName="Text", Used=1).Create()

            Domoticz.Log("Devices created")

        updateInterval = int(Parameters["Mode5"])
        
        if updateInterval < 180:
            if updateInterval < 10: updateInterval == 10
            Domoticz.Log("Update interval set to " + str(updateInterval) + " (minimum is 10 seconds)")
            Domoticz.Heartbeat(updateInterval)
        else:
            Domoticz.Heartbeat(180)
        
        if self.debug == True:
            DumpConfigToLog()
            

        

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        
        out = self.run()
        Domoticz.Debug(out)
        info = out.split("|")
        percent = float(info[0])
        plugged = "Plugged In" if info[1] == "CONNECTED" else "Not Plugged In"
        charging = "Charging" if info[2] == "CHARGING" else "Not Charging"

        UpdateDevice(1, 1, percent)        
        UpdateDevice(2, 1, plugged)        
        UpdateDevice(3, 1, charging)        



global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()



# Update Device into database
def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if ((Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (AlwaysUpdate == True)):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
