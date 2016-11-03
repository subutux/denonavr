import requests
import xml.etree.ElementTree as ET
#Constants
URL="http://{ip}{get}"
STATUS="/goform/formMainZone_MainZoneXml.xml?_=&ZoneName={zone}"
STATUS_LITE="/goform/formMainZone_MainZoneXmlStatusLite.xml" #?
ZONE2_STATUS="goform/formMainZone_MainZoneXml.xml?_=&ZoneName=ZONE2" # ?
ZONE2_STATUS_LITE="goform/formZone2_Zone2XmlStatusLite.xml"
MAINZONE_INPUT="/MainZone/index.put.asp?cmd0={cmd}"
## Only supports actions without return :(
HTTP_TELNET_CMD="/goform/formiPhoneAppDirect.xml?{telnetcmd}"

class Denon():
    def __init__(self,ip,zone="MAINZONE"):
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
        
        updateStatus()
        
    def updateStatus(self):
        """
        Update the status
        """
        r = requests.get(URL.format(ip=self.ip,get=STATUS.format(zone=self.zone)))
        tree = ET.fromstring(r.text)
        for child in tree:
            self._status[child.tag] = child[0].text
        
        return True
    
    def exec(self,telnetcmd):
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
    def name(self):
        return self._status["FriendlyName"]
    @property
    def zoneName(self):
        return self._status["RenameZone"]
    @property
    def input(self):
        return self._status["inputFuncSelect"]
    
    