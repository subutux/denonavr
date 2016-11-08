import requests
import xml.etree.ElementTree as ET
__version__ = "0.5b3"
#Constants
URL="http://{ip}{get}"
STATUS="/goform/formMainZone_MainZoneXml.xml?ZoneName={zone}"
NETSTATUS="/goform/formNetAudio_StatusXml.xml?ZoneName={zone}"
NETCMD="/NetAudio/index.put.asp"
CH_STATUS="/goform/formMainZone_MainZoneXmlStatus.xml"
STATUS_LITE="/goform/formMainZone_MainZoneXmlStatusLite.xml" #?
ZONE2_STATUS="goform/formMainZone_MainZoneXml.xml?_=&ZoneName=ZONE2" # ?
ZONE2_STATUS_LITE="goform/formZone2_Zone2XmlStatusLite.xml"
MAINZONECMD="/MainZone/index.put.asp"
## Only supports actions without return :(
HTTP_TELNET_CMD="/goform/formiPhoneAppDirect.xml?{telnetcmd}"
#SET_VOL="/goform/formiPhoneAppVolume.xml?{"
# The maximum volume allowed to be set.
## -> normally, the max volume is arround 100-110
##    Wich is loud! (very!) We set a max here
##    to spare our ears when things go south
MAX_VOLUME=50

def Connect(ip,zone="MAIN+ZONE"):
    """
    Returns a instance of Zone
    """
    return Zone(ip,zone)


class Zone():
    def __init__(self,ip,zone="MAIN+ZONE"):
        self.ip = ip
        self.zone = zone
        self._status = {
            "FriendlyName" : "",
            "Power" : "",
            "ZonePower" : "",
            "RenameZone" : "",
            "TopMenuLink" : "",
            "VideoSelectDisp" : "",
            "VideoSelect" : "",
            "VideoSelectOnOff" : "",
            "VideoSelectLists" : "",
            "AddSourceDisplay" : "",
            "ModelId" : "",
            "BrandId" : "",
            "SalesArea" : "",
            "InputFuncSelect" : "",
            "NetFuncSelect" : "",
            "selectSurround" : "",
            "VolumeDisplay" : "",
            "MasterVolume" : 0,
            "Mute" : "",
            "RemoteMaintenance" : "",
            "SubwooferDisplay" : "",
            "Zone2VolDisp" : ""
        }
        self._inputs = {}
        self._szLines = []
        self.updateStatus()
        self.updateInputs()
    def updateStatus(self):
        """
        Update the status of this denon reciever
        """
        try:
            r = requests.get(URL.format(ip=self.ip,get=STATUS.format(zone=self.zone)))
        except requests.exceptions.RequestException:
            return False

        tree = ET.fromstring(r.text)
        for child in tree:
            self._status[child.tag] = child[0].text
        
        self._volume = self._status["MasterVolume"]
        self._szLines = []
        try:
            r = requests.get(URL.format(ip=self.ip,get=NETSTATUS.format(zone=self.zone)))
        except requests.exceptions.RequestException:
            return False

        tree = ET.fromstring(r.text)
        for line in tree.findall("szLine")[0]:
            self._szLines.append(line.text)
        return True
    def updateInputs(self):
        """
        Get the channel list & determine it's friendly name & if it's hidden or not
        """
        try:
            r = requests.get(URL.format(ip=self.ip,get=CH_STATUS))
        except requests.exceptions.RequestException:
            return False

        tree = ET.fromstring(r.text)
        
        # Loop over the AVR Inputs, their RenameSource, SourceDelete & add them to self._inputs
        for inputAvr,rename,use in zip(tree.findall("InputFuncList")[0],
                                    tree.findall("RenameSource")[0],
                                    tree.findall('SourceDelete')[0]):
            #check if we need to add it
            if use.text == "USE":
                # get friendly name & add                             Fix the extra spaces at the end
                self._inputs[inputAvr.text] = { "friendly_name" : ' '.join(rename[0].text.split())  }
                # Some extras:

                if inputAvr.text == "Bluetooth":
                    self._inputs[inputAvr.text]["NetName"] = "BT"
                if inputAvr.text == "CBL/SAT":
                    self._inputs[inputAvr.text]["NetName"] = "SAT"
        ## Special Inputs, according to ModelId
        ## For more info, see index.js L 434
        ### EnModelARX10 & EnModelNR15
        if self._status["ModelId"] in ("1","7"):
            self._inputs["Online Music"] = {
            "friendly_name": "Online Music",
            "NetName" : "NETHOME"
            }
            self._inputs["Tuner"] = {
            "friendly_name": "Tuner",
            "NetName" : "TUNER"
            }
            self._inputs["Internet Radio"] = {
            "friendly_name": "Internet Radio",
            "NetName" : "IRP"
            }


    def isVolumeAbsolute(self):
        """
        Check if the volume returned is absolute.
        """
        if self._status["VolumeDisplay"] == "Absolute":
            return True
        else:
            return False

    @property
    def state(self):
        """
        Returns the current state of the denon reciever.
        Can be ON or STANDBY
        """
        return self._status["Power"]
    
    @property
    def nowPlaying(self):
        """
        returns the Playing information.

        If we detect a NetInput, check for the NETSTATUS for more detailled
        information.
        """
        if self._status['InputFuncSelect'] in ('Online Music','iPod/USB','Bluetooth'):
            if self._status['InputFuncSelect'] == "Bluetooth":
                art = "http://{ip}/img/album%20art_BT.png"
            else:
                art = "http://{ip}/NetAudio/art.asp-jpg"
            return {
            "INPUT": self._status['InputFuncSelect'],
            "SONG": self._szLines[1],
            "ARTIST": self._szLines[2],
            "ALBUM" : self._szLines[3],
            "ALBUM_ART": art.format(ip=self.ip)
            }
        else:
            return {
            "INPUT": self._status['InputFuncSelect'],
            "SONG": None,
            "ARTIST": None,
            "ALBUM" : None,
            "ALBUM_ART": None
            }

    @property
    def name(self):
        """
        Return the name of this denon avr
        """
        return self._status["FriendlyName"]
    @property
    def zoneName(self):
        """
        return the zone name
        """
        return self._status["RenameZone"]
    @property
    def input(self):
        """
        Return the current input/source
        """
        return self._status["InputFuncSelect"]
    
    @property
    def volume(self):
        """
        Return the current volume.
        """
        vol = self._status["MasterVolume"]

        if self.isVolumeAbsolute():
            if vol == "--":
                vol = -80.0
            vol = float(vol) + 80
            return float("{0:.2f}".format(vol))
        else:
            return float(vol); 
    
    @volume.setter
    def volume(self,value):
        """
        If the value is larger then MAX_VOLUME,
        set it to MAX_VOLUME.
        """
        if value > MAX_VOLUME:
            value = MAX_VOLUME
        if self.isVolumeAbsolute():
            vol = float(value) - 80
            vol = float("{0:.2f}".format(vol))
            return self.netCmd(mcmd="PutMasterVolumeSet",cmd=str(vol)) 
    
    @property
    def volume_percent(self):
        """
        Get the volume in percentage. Use the MAX_VOLUME
        to calculate the percentage.
        """
        clean_vol = self.volume
        return round((clean_vol / MAX_VOLUME) * 100)
    
    
    @volume_percent.setter
    def volume_percent(self,value):
        """
        Convert the value to the actual volume & set it
        as the current volume.
        """
        vol = (float(value) * MAX_VOLUME ) / 100
        self.volume = vol

    def volume_up(self):
        """
        Increase the volume
        """
        return self.netCmd(">",mcmd="PutMasterVolumeBtn")
    
    def volume_down(self):
        """
        Decrease the volume
        """
        return self.netCmd("<",mcmd="PutMasterVolumeBtn")

    @property
    def mute(self):
        """
        Return true if muted
        """
        return self._status["Mute"] is "off"

    @mute.setter
    def mute(self,mute):
        """
        set mute based on true/false
        """
        self.zoneCmd(('on' if mute else 'off'),mcmd="PutVolumeMute")
    
    def play(self):
        """
        Send the play button
        """
        self.telCmd("NS9A")

    def pause(self):
        """
        send the pause button
        """
        self.telCmd("NS9B")

    def stop(self):
        """
        send the stop button
        """
        self.telCmd("NS9C")

    def next_track(self):

        """
        send the next button
        """
        self.telCmd("NS9D")

    def previous_track(self):
        """
        send the previous button
        """
        self.telCmd("NS9E")

    def setInput(self,inputFunction):
        """
        Set the current input/source for the reciever

        It tries to find the correct input based on the
        inputFunction & the self._inputs
        """
        inputF = None
        if inputFunction not in self._inputs:
            # try to check if it's a friendly_name
            for inp in self._inputs:
                if self._inputs[inp]["friendly_name"] == inputFunction:
                    inputF = inp
                    break

        else:
            inputF = inputFunction
        
        if inputF is None:
            raise Exception("Unknown input {}".format(inputFunction))

        if "NetName" in self._inputs[inputF]:
            print("Got NetName")
            inputF = self._inputs[inputF]["NetName"]
        
        return self.zoneCmd(cmd=inputF,mcmd="PutZone_InputFunction")

    @property
    def inputs(self):
        
        return [inp for inp in self._inputs]
    
    def turnOn(self):
        """
        Turn the system On
        """
        return self.zoneCmd("ON",mcmd="PutSystem_OnStandby")
    
    def turnOff(self):
        """
        Set the system in Standby/off
        """
        return self.zoneCmd("STANDBY",mcmd="PutSystem_OnStandby")

    def netCmd(self,cmd,mcmd="PutNetAudioCommand"):
        """
        Sends a netAudioCommand.

        There are more supported. See below.

        Commands
        ========

        Commands can be executed is sequence.
        for example. to go 1 down & 1 right
        you post the following data:

        cmd0=PutNetAudioCommand/CurDown
        cmd1=osThreadSleep/50
        cmd2=PutNetAudioCommand/CurRight

        Following are known to work:

        PutNetAudioCommand/
        -------------------
        * CurEnter
        * CurUp
        * CurDown
        * CurLeft
        * CurRight
        * CmdStop
        * CmdPageUp
        * CmdPageDown
        * UsbRepOn
        * UsbRepAll
        * UsbRepOff
        * UsbRanOn
        * UsbRanOff
        * Search+([1-9]|[A-Z])
        
        PutMasterVolumeBtn/
        -------------------
        * `>` Volume Up
        * `<` Volume Down

        PutVolumeMute/
        -------------------
        * TOGGLE
        osThreadSleep/
        -------------
        * `int()` (`50` is used in the WebUI)

        aspMainZone_WebUpdateStatus/
        ----------------------------
        UNKNOWN
        """
        postData = {
        "cmd0": "{mcmd}/{cmd}".format(mcmd=mcmd,cmd=cmd)
        }
        print(postData)
        try:
            r = requests.post(URL.format(ip=self.ip,get=NETCMD),data=postData)
        except requests.exceptions.RequestException:
            return False
    def zoneCmd(self,cmd,mcmd="PutSystem_OnStandby"):
        """
        Sends a PutSystem_OnStandby command
        """
        getData = {
        "cmd0": "{mcmd}/{cmd}".format(mcmd=mcmd,cmd=cmd),
        "cmd1": "aspMainZone_WebUpdateStatus/"
        }
        try:
            r = requests.get(URL.format(ip=self.ip,get=MAINZONECMD),params=getData)
            print(r.text,r.url)
        except requests.exceptions.RequestException:
            return False

    def telCmd(self,telnetcmd):
        """
        Execute Telnet fire & forget (or better, fire & hope for the best) calls over http
        """
        try:
            r = requests.get(URL.format(ip=self.ip,get=HTTP_TELNET_CMD.format(telnetcmd=telnetcmd)))
            if r.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException:
            return False