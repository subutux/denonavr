# denonavr
A python library to interact with an Denon AVR

## denonavr.denon

### Usage

```python
from denonavr import denon
#                        your denon ip
myDenon = denon.Connect('192.168.1.20')
```

See the file [denon.py](denonavr/denon.py) for possible options,
or use pydoc to view the documentation:

```bash
pydoc denonavr.denon
```

## Denon-cli

### Usage:

```
usage: denonavr-cli.py [-h] -H HOST [-z ZONE] CMD

Remote Denon controller

positional arguments:
  CMD                   A telnet command to execute

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  IP or host of the denon system to connect to
  -z ZONE, --zone ZONE  The zone to use (default: MAINZONE)
```