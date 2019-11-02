#!/usr/bin/env python3
from setuptools import setup
import re
 
 
version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('denonavr/denon.py').read(),
    re.M
    ).group(1)
 
 
with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")
 
 
setup(
    name="denonavr",
    version=version,
    packages = ["denonavr"],
    description="Denon AVR controller",
    long_description=long_descr,
   
    entry_points = {
        "console_scripts": ['denonavr-cli = denonavr.cli:main']
    },
    install_requires= [
    
        "requests==2.20.0"
        
    ]
)
