from . import denon as Denon
import argparse

def main():
    
	p = argparse.ArgumentParser(description="Remote Denon controller")
	p.add_argument('-H','--host',help="IP or host of the denon system to connect to",required=True)
	p.add_argument('-z','--zone',help="The zone to use (default: MAINZONE",default="MAINZONE")
	p.add_argument('CMD',help="A telnet command to execute")
	args = p.parse_args();
	
	MAINZONE=Denon.Connect(args.host,args.zone)
	MAINZONE.telCmd(args.CMD)
