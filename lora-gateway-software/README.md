# DeviceHive LoRa Gateway software
This is a simple Python project which sould be run from frimware part of this gateway with
[Arduino Bridge](https://www.arduino.cc/en/Reference/YunBridgeLibrary). It uses [DeviceHive]
(https://github.com/devicehive/devicehive-python) library to connect to DeviceHive server and
communicates with the firmware part of this gateway using stdin/stdout. To configure server
URL and credentials there is a simple HTTP server on port 8000.

