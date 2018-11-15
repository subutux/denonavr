import requests
import logging
import xml.etree.ElementTree as ET
__version__ = "0.7b3"
# Constants
URL = "http://{ip}{get}"
STATUS = "/goform/formMainZone_MainZoneXml.xml?ZoneName={zone}"
NETSTATUS = "/goform/formNetAudio_StatusXml.xml?ZoneName={zone}"
NETCMD = "/NetAudio/index.put.asp"
CH_STATUS = "/goform/formMainZone_MainZoneXmlStatus.xml"
STATUS_LITE = "/goform/formMainZone_MainZoneXmlStatusLite.xml"
ZONE2_STATUS = "goform/formMainZone_MainZoneXml.xml?_=&ZoneName=ZONE2"
ZONE2_STATUS_LITE = "goform/formZone2_Zone2XmlStatusLite.xml"
MAINZONECMD = "/MainZone/index.put.asp"
# Only supports actions without return :(
HTTP_TELNET_CMD = "/goform/formiPhoneAppDirect.xml?{telnetcmd}"
# SET_VOL="/goform/formiPhoneAppVolume.xml?{"
# The maximum volume allowed to be set.
# -> normally, the max volume is arround 100-110
#    Wich is loud! (very!) We set a max here
#    to spare our ears when things go south
MAX_VOLUME = 50
_LOGGER = logging.getLogger(__name__)


def Connect(ip, zone="MAIN+ZONE"):
    """
    Returns a instance of Zone
    """
    return Zone(ip, zone)


class Zone():
    def __init__(self, ip, zone="MAIN+ZONE"):
        self.ip = ip
        self.zone = zone
        self._status = {
            "FriendlyName": "",
            "Power": "",
            "ZonePower": "",
            "RenameZone": "",
            "TopMenuLink": "",
            "VideoSelectDisp": "",
            "VideoSelect": "",
            "VideoSelectOnOff": "",
            "VideoSelectLists": "",
            "AddSourceDisplay": "",
            "ModelId": "",
            "BrandId": "",
            "SalesArea": "",
            "InputFuncSelect": "",
            "NetFuncSelect": "",
            "selectSurround": "",
            "VolumeDisplay": "",
            "MasterVolume": 0,
            "Mute": "",
            "RemoteMaintenance": "",
            "SubwooferDisplay": "",
            "Zone2VolDisp": ""
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
            url = URL.format(ip=self.ip, get=STATUS.format(zone=self.zone))
            _LOGGER.debug("GET {url}".format(url=url))
            r = requests.get(url)
            # _LOGGER.debug("Recieve")
            # _LOGGER.debug(r.text)
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Unable to fetch the status from {}".format(self.ip))
            _LOGGER.debug("requests.exceptions.RequestException: {}".format(e))
            return False
        tree = ET.fromstring(r.text)
        for child in tree:
            _LOGGER.debug("{} = {}".format(child.tag, child[0].text))
            self._status[child.tag] = child[0].text
        self._volume = self._status["MasterVolume"]
        self._szLines = []
        try:
            url = URL.format(ip=self.ip, get=NETSTATUS.format(zone=self.zone))
            _LOGGER.debug("GET {url}".format(url=url))
            r = requests.get(url)
            # _LOGGER.debug("Recieve")
            # _LOGGER.debug(r.text)
        except requests.exceptions.RequestException as e:
            _LOGGER.error(
                "Unable to fetch the netstatus from {}".format(self.ip)
            )
            _LOGGER.debug("requests.exceptions.RequestException: {}".format(e))
            return False

        tree = ET.fromstring(r.text)
        for line in tree.findall("szLine")[0]:
            _LOGGER.debug("status line {}".format(line.text))
            self._szLines.append(line.text)
        return True

    def updateInputs(self):
        """
        Get the channel list & determine it's friendly name
        & if it's hidden or not
        """
        try:
            url = URL.format(ip=self.ip, get=CH_STATUS)
            _LOGGER.debug("GET {url}".format(url=url))
            r = requests.get(url)
            # _LOGGER.debug("Recieve")
            # _LOGGER.debug(r.text)
        except requests.exceptions.RequestException as e:
            _LOGGER.error(
                "Unable to fetch the status from {}:".format(self.ip)
                )
            _LOGGER.debug(
                "requests.exceptions.RequestException: {}".format(e)
                )
            return False

        tree = ET.fromstring(r.text)

        # Loop over the AVR Inputs, their RenameSource, SourceDelete & add them
        # to self._inputs
        for inputAvr, rename, use in zip(tree.findall("InputFuncList")[0],
                                         tree.findall("RenameSource")[0],
                                         tree.findall('SourceDelete')[0]):
            _LOGGER.debug("Got input {}({}) -> {}".format(
                rename[0].text,
                use.text,
                inputAvr.text
                ))
            # check if we need to add it
            if use.text != "DEL":
                self._inputs[inputAvr.text] = {
                    "friendly_name": ' '.join(rename[0].text.split())
                    }
                # Most of the inputs need a command name other then
                # the actual input name
                if inputAvr.text == "Bluetooth":
                    _LOGGER.debug("Adding NetName for bluetooth")
                    self._inputs[inputAvr.text]["NetName"] = "BT"
                if inputAvr.text == "CBL/SAT":
                    _LOGGER.debug("Adding NetName for CBL/SAT")
                    self._inputs[inputAvr.text]["NetName"] = "SAT"
                if inputAvr.text == "Media Player":
                    _LOGGER.debug("Adding NetName for Media Player")
                    self._inputs[inputAvr.text]["NetName"] = "MPLAY"
                if inputAvr.text == "DVD/Blu-ray":
                    _LOGGER.debug("Adding NetName for DVD/Blu-ray")
                    self._inputs[inputAvr.text]["NetName"] = "DVD"
                if inputAvr.text == "Blu-ray":
                    _LOGGER.debug("Adding NetName for Blu-ray")
                    self._inputs[inputAvr.text]["NetName"] = "BD"
                if inputAvr.text == "iPod/USB":
                    _LOGGER.debug("Adding NetName for iPod/USB")
                    self._inputs[inputAvr.text]["NetName"] = "USB/IPOD"
                if inputAvr.text == "TV Audio":
                    _LOGGER.debug("Adding NetName for TV Audio")
                    self._inputs[inputAvr.text]["NetName"] = "TV"
                if inputAvr.text == "Tuner":
                    _LOGGER.debug("Adding NetName for Tuner")
                    self._inputs[inputAvr.text]["NetName"] = "TUNER"
                if inputAvr.text == "Online Music":
                    _LOGGER.debug("Adding NetName for Online Music")
                    self._inputs[inputAvr.text]["NetName"] = "NETHOME"
                if inputAvr.text == "Phono":
                    _LOGGER.debug("Adding NetName for Phono")
                    self._inputs[inputAvr.text]["NetName"] = "PHONO"
                if inputAvr.text == "HD Radio":
                    _LOGGER.debug("Adding NetName for HD Radio")
                    self._inputs[inputAvr.text]["NetName"] = "HDRADIO"
        # Special Inputs, according to ModelId
        # For more info, see index.js L 434
        #   EnModelARX10 & EnModelNR15
        if self._status["ModelId"] in ("1", "7", "2", "3", "8", "9"):
            _LOGGER.debug(
                "Got one of model EnModelARX10 EnModelNR15  EnModelAVRX2\
                EnModelAVRX30  EnModelNR16 EnModelSR50, adding IRP"
                )
            self._inputs["Internet Radio"] = {
                "friendly_name": "Internet Radio",
                "NetName": "IRP"
            }
        #  EnModelAVRX2 EnModelAVRX30  EnModelNR16 EnModelSR50
        elif self._status["ModelId"] in ("2", "3", "8", "9"):
            _LOGGER.debug(
                "Got one of models  EnModelAVRX2 EnModelAVRX30  EnModelNR16\
                EnModelSR50, adding SERVER"
                )
            self._inputs["Media Server"] = {
                "friendly_name": "Media Server",
                "NetName": "SERVER"
            }
            # Don't know if these are returned by CH_STATUS
            # self._inputs["AUX1"] = {
            #     "friendly_name": "AUX1",
            #     "NetName": "AUX1"
            # }
            # self._inputs["AUX2"] = {
            #     "friendly_name": "AUX2",
            #     "NetName": "AUX2"
            # }

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
        if self._status['InputFuncSelect'] in ('Online Music',
                                               'iPod/USB',
                                               'Bluetooth'):
            if self._status['InputFuncSelect'] == "Bluetooth":
                art = "http://{ip}/img/album%20art_BT.png"
            else:
                art = "http://{ip}/NetAudio/art.asp-jpg"
            return {
                "INPUT": self._status['InputFuncSelect'],
                "SONG": self._szLines[1],
                "ARTIST": self._szLines[2],
                "ALBUM": self._szLines[3],
                "ALBUM_ART": art.format(ip=self.ip)
            }
        else:
            return {
                "INPUT": self._status['InputFuncSelect'],
                "SONG": None,
                "ARTIST": None,
                "ALBUM": None,
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
            return float(vol)

    @volume.setter
    def volume(self, value):
        """
        If the value is larger then MAX_VOLUME,
        set it to MAX_VOLUME.
        """
        if value > MAX_VOLUME:
            value = MAX_VOLUME
        if self.isVolumeAbsolute():
            vol = float(value) - 80
            vol = float("{0:.2f}".format(vol))
            return self.netCmd(mcmd="PutMasterVolumeSet", cmd=str(vol))

    @property
    def volume_percent(self):
        """
        Get the volume in percentage. Use the MAX_VOLUME
        to calculate the percentage.
        """
        clean_vol = self.volume
        return round((clean_vol / MAX_VOLUME) * 100)

    @volume_percent.setter
    def volume_percent(self, value):
        """
        Convert the value to the actual volume & set it
        as the current volume.
        """
        vol = (float(value) * MAX_VOLUME) / 100
        self.volume = vol

    def volume_up(self):
        """
        Increase the volume
        """
        return self.netCmd(">", mcmd="PutMasterVolumeBtn")

    def volume_down(self):
        """
        Decrease the volume
        """
        return self.netCmd("<", mcmd="PutMasterVolumeBtn")

    @property
    def mute(self):
        """
        Return true if muted
        """
        return self._status["Mute"] == "off"

    @mute.setter
    def mute(self, mute):
        """
        set mute based on true/false
        """
        self.zoneCmd(('on' if mute else 'off'), mcmd="PutVolumeMute")

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

    def setInput(self, inputFunction):
        """
        Set the current input/source for the reciever

        It tries to find the correct input based on the
        inputFunction & the self._inputs
        """
        inputF = None
        if inputFunction not in self._inputs:
            _LOGGER.debug("Unable to find input. Searching as friendly_name")
            # try to check if it's a friendly_name
            for inp in self._inputs:
                if self._inputs[inp]["friendly_name"] == inputFunction:
                    _LOGGER.debug("Got it! {}".format(inp))
                    inputF = inp
                    break

        else:
            inputF = inputFunction

        if inputF is None:
            _LOGGER.debug("Unable to find input {}".format(inputFunction))
            raise Exception("Unknown input {}".format(inputFunction))

        if "NetName" in self._inputs[inputF]:
            inputF = self._inputs[inputF]["NetName"]
            _LOGGER.debug("Found a NetName, using that. ({})".format(inputF))

        return self.zoneCmd(cmd=inputF, mcmd="PutZone_InputFunction")

    @property
    def inputs(self):

        return [self._inputs[inp]["friendly_name"] for inp in self._inputs]

    def turnOn(self):
        """
        Turn the system On
        """
        return self.zoneCmd("ON", mcmd="PutSystem_OnStandby")

    def turnOff(self):
        """
        Set the system in Standby/off
        """
        return self.zoneCmd("STANDBY", mcmd="PutSystem_OnStandby")

    def netCmd(self, cmd, mcmd="PutNetAudioCommand"):
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
            "cmd0": "{mcmd}/{cmd}".format(mcmd=mcmd, cmd=cmd)
        }
        print(postData)
        try:
            _LOGGER.debug("Sending POST with data: {}".format(str(postData)))
            r = requests.post(
                URL.format(ip=self.ip, get=NETCMD), data=postData
                )
            _LOGGER.debug("status: {} response: {}, url: {}".format(
                r.status_code,
                r.text,
                r.url
                ))
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Unable to send command to {}".format(self.ip))
            _LOGGER.debug("requests.exceptions.RequestException: {}".format(e))
            return False

    def zoneCmd(self, cmd, mcmd="PutSystem_OnStandby"):
        """
        Sends a PutSystem_OnStandby command
        """
        getData = {
            "cmd0": "{mcmd}/{cmd}".format(mcmd=mcmd, cmd=cmd),
            "cmd1": "aspMainZone_WebUpdateStatus/"
        }
        try:

            _LOGGER.debug("Sending GET with data: {}".format(str(getData)))
            r = requests.get(
                URL.format(ip=self.ip, get=MAINZONECMD), params=getData
                )
            _LOGGER.debug(
                "status: {} response: {}, url: {}".format(
                    r.status_code,
                    r.text,
                    r.url
                    )
                )
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Unable to send command to {}".format(self.ip))
            _LOGGER.debug("requests.exceptions.RequestException: {}".format(e))
            return False

    def telCmd(self, telnetcmd):
        """
        Execute Telnet fire & forget (or better, fire & hope for the best)
        calls over http
        """
        try:
            _LOGGER("Executing command {}".format(telnetcmd))
            r = requests.get(
                URL.format(ip=self.ip, get=HTTP_TELNET_CMD.format(
                    telnetcmd=telnetcmd
                    ))
                )
            _LOGGER.debug(
                "status: {} response: {}, url: {}".format(
                    r.status_code,
                    r.text,
                    r.url
                    )
                )
            if r.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Unable to send command to {}".format(self.ip))
            _LOGGER.debug("requests.exceptions.RequestException: {}".format(e))
            return False
