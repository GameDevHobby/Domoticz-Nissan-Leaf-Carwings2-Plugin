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
        <param field="Mode4" label="API interval (should be infrequent, in sec)" width="30px" required="true" default="900"/>
        <param field="Mode5" label="Plugin Update interval (sec)" width="30px" required="true" default="30"/>
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
import datetime

class BasePlugin:
    enabled = False
    def __init__(self):
        self.debug = False
        self.last_result = None
        self.updateInterval = 600
        self.apiInterval = 900
        self.lastApiUpdateTime = datetime.datetime.min # force recheck on start

        return

    def run(self, result=None):
        username = Parameters["Username"]
        password = Parameters["Password"]
        region = Parameters["Mode1"]
        cmd = "python " + Parameters["HomeFolder"] + "car.py -u " + username + " -p " + password + " -r " + region 
        if result is not None:
            cmd = cmd + " -c result -a " + result
        else:
            cmd = cmd + " -c update"

        Domoticz.Debug(cmd.replace(password, "***************"))

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        out = out.decode("utf-8")
        err = err.decode("utf-8")
        
        #Domoticz.Debug("ReturnCode: " + str(p.returncode))
        #Domoticz.Debug("out: " + out)
        #Domoticz.Debug("err: " + err)
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

        self.updateInterval = int(Parameters["Mode5"])
        self.apiInterval = int(Parameters["Mode4"])
        self.lastApiUpdateTime = datetime.datetime.min # force recheck on start

        if self.updateInterval < 600:
            if self.updateInterval < 30: 
                self.updateInterval == 30
            Domoticz.Log("Update interval set to " + str(self.updateInterval) + " (minimum is 30 seconds)")
            Domoticz.Heartbeat(self.updateInterval)
        else:
            self.updateInterval = 600
            Domoticz.Heartbeat(self.updateInterval)
        
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
        out = None
        if self.last_result is not None:
            Domoticz.Debug("Checking on update.")
            out = ""
            try:
                self.lastApiUpdateTime = datetime.datetime.now()
                out = self.run(self.last_result)
                Domoticz.Debug("Result: " + out)
            except:
                Domoticz.Debug("Couldn't communicate with car: ")
                out = "-99|NO COMMUNICATION|UNKNOWN"

            if out is None or "None" in out:
                #self.last_result = None
                return

            info = out.split("|")
            percent = float(info[0])
            plugged = info[1].rstrip()#"Plugged In" if info[1] == "CONNECTED" else "Not Plugged In"
            charging = info[2].rstrip()#"Charging" if info[2] == "NORMAL_CHARGING" else "Not Charging"

            UpdateDevice(1, 1, percent, True)        
            UpdateDevice(2, 1, plugged)        
            UpdateDevice(3, 1, charging)        

            self.last_result = None
            #Domoticz.Heartbeat(self.updateInterval)
        else:
            timedelta = datetime.timedelta(seconds = self.apiInterval)
            if self.lastApiUpdateTime + timedelta < datetime.datetime.now():
                Domoticz.Debug("Updating...")
                self.last_result = self.run()
                Domoticz.Debug("Result: " + self.last_result)
                #Domoticz.Heartbeat(10)
            else:
                Domoticz.Debug("Not updating yet... Will update at: " + str(self.lastApiUpdateTime + timedelta)) 


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
        if Parameters[x] != "" and x.lower() != "password":
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
