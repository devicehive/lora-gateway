# DeviceHive LoRa Gateway firmware
This is a firmware for the microcontroller part of Dragino gateway. It can be build and flash
with Arduino IDE. See deatils [here](http://www.dragino.com/downloads/downloads/UserManual/LG01_LoRa_Gateway_User_Manual.pdf).

This firmware receives/sents data from LoRa radio and transmits it to Python part of this
gateway with stdin/stdout using bridge API(class Process). It also starts Python part on
firmware start.
