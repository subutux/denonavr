import requests
import xml.etree.ElementTree as ET
__version__ = "0.1b1"
#Constants
URL="http://{ip}{get}"
STATUS="/goform/formMainZone_MainZoneXml.xml?ZoneName={zone}"
NETSTATUS="/goform/formNetAudio_StatusXml.xml?ZoneName={zone}"
NETCMD="/NetAudio/index.put.asp"
CH_STATUS="/goform/formMainZone_MainZoneXmlStatus.xml"
STATUS_LITE="/goform/formMainZone_MainZoneXmlStatusLite.xml" #?
ZONE2_STATUS="goform/formMainZone_MainZoneXml.xml?_=&ZoneName=ZONE2" # ?
ZONE2_STATUS_LITE="goform/formZone2_Zone2XmlStatusLite.xml"
MAINZONE_INPUT="/MainZone/index.put.asp?cmd0={cmd}"
## Only supports actions without return :(
HTTP_TELNET_CMD="/goform/formiPhoneAppDirect.xml?{telnetcmd}"
SET_VOL="/goform/formiPhoneAppVolume.xml?{"
# The maximum volume allowed to be set.
## -> normally, the max volume is arround -60dB
##    Wich is loud! (very!) We set a max here
##    to spare our ears when things go south
# So , here we have a max of -50dB
MAX_VOLUME_dB=50

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
        Update the status
        """
        r = requests.get(URL.format(ip=self.ip,get=STATUS.format(zone=self.zone)))
        tree = ET.fromstring(r.text)
        for child in tree:
            self._status[child.tag] = child[0].text
        
        self._volume = self._status["MasterVolume"]

        r = requests.get(URL.format(ip=self.ip,get=NETSTATUS.format(zone=self.zone)))
        tree = ET.fromstring(r.text)
        for line in tree.findall("szLine")[0]:
            self._szLines.append(line.text)
        return True
    def updateInputs(self):
        """
        Get the channel list & determine it's friendly name & if it's hidden or not
        """
        r = requests.get(URL.format(ip=self.ip,get=CH_STATUS))
        tree = ET.fromstring(r.text)
        
        # Loop over the AVR Inputs, their RenameSource, SourceDelete & add them to self._inputs
        for inputAvr,rename,use in zip(tree.findall("InputFuncList")[0],
                                    tree.findall("RenameSource")[0],
                                    tree.findall('SourceDelete')[0]):
            #check if we need to add it
            if use.text == "USE":
                # get friendly name & add                             Fix the extra spaces at the end
                self._inputs[inputAvr.text] = { "friendly_name" : ' '.join(rename[0].text.split())  }
        
    def cmd(self,telnetcmd):
        """
        Execute Telnet fire & forget (or better, fire & hope for the best) calls over http
        """
        
        r = requests.get(URL.format(ip=self.ip,get=HTTP_TELNET_CMD.format(telnetcmd=telnetcmd)))
        if r.status_code == 200:
            return True
        else:
            return False
    
    @property
    def state(self):
        return self._status["Power"]
    
    @property
    def nowPlaying(self):
        """
        returns the Playing information.

        If we detect a NetInput, check for the NETSTATUS for more detailled
        information.
        """
        if self._status['InputFuncSelect'] in ('Online Music','iPod/USB','Bluetooth'):
            return {
            "INPUT": self._status['InputFuncSelect'],
            "SONG": self._szLines[1],
            "ARTIST": self._szLines[2],
            "ALBUM" : self._szLines[3],
            "ALBUM_ART": "http://{ip}/NetAudio/art.asp-jpg".format(ip=self.ip)
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
        return self._status["FriendlyName"]
    @property
    def zoneName(self):
        return self._status["RenameZone"]
    @property
    def input(self):
        return self._status["InputFuncSelect"]
    
    @property
    def volume(self):
        return "{volume} dB".format(volume=self._status["MasterVolume"])
    @property
    def volume_percent(self):
        #                                 remove "-"
        #                                        |   remove dB
        #                                        |    |
        clean_vol = self._status["MasterVolume"][1:][:2]
        clean_vol = int(clean_vol)
        return round((clean_vol / MAX_VOLUME_dB) * 100,2)
    
    
    @volume.setter
    def volume(self,value):
        # Detect if we need to handle a percent value
        # or a dB value
        if value[:2] == "dB":
            self._volume == value[:2]
            self.cmd("SI")
    def netCmd(self,cmd):
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
        "cmd0": "PutNetAudioCommand/{cmd}".format(cmd=cmd)
        }
        r = requests.post(URL.format(ip=self.ip,get=NETCMD),data=postData)
