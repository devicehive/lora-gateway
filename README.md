# DeviceHive [LoRa](https://www.lora-alliance.org/) gateway
This project implements LoRa gateway using DeviceHive cloud service. It is a
transparent gateway between DeviceHive cloud service and LoRa radio.Everything
which LoRa receives sends to DeviceHive server as notifications. Command 'lora'
transmit 'data' field into LoRa. It is a transparent gateway between DeviceHive
cloud service and LoRa radio.

# Hardware
This project uses [Dragino LG01](http://www.dragino.com/products/lora/item/117-lg01-p.html)
gateway as a reference hardware.

# Installation
Make sure that gateway firmware version is 4.3 or newer. You can get new
firmware [here](http://www.dragino.com/downloads/index.php?dir=motherboards/ms14/Firmware/IoT/)
- Install Python DeviceHive library. Connect with ssh to the router
(`ssh root@10.130.1.1`, password `dragino` by default) and run:
```bash
curl -SL https://github.com/devicehive/devicehive-python/archive/2.1.0.tar.gz | tar zx
cd devicehive-python-2.1.0/
python setup.py install
cd ..
rm -rf devicehive-python-2.1.0/
```
- Copy gateway package:
```bash
mkdir -p /opt/devicehive && curl -SL https://github.com/devicehive/lora-gateway/releases/download/v0.0.1/gateway.tar.gz | tar zx -C /opt/devicehive
```
- Install it with:
```bash
/opt/devicehive/gateway.py install
```
This command flashes firmware into gateway. Firmware automatically boots on power on and
starts Python part.
- Configure gateway with DeviceHive server URL, credentilals and LoRa frequency. Open web
browser http://gateway-ip:8000 and enter settings there. Click on `save`.

To remove it completly, remove `/opt/devicehive` directory,
`pip uninstall devicehive` and flash(or just leave it) any new firmware to the
microcontroller part of the gateway.

# Usage
Gateway boots automatically on power on. It works on specfied in config frequency and
receives all LoRa packages which send to DeviceHive server as notifications. Notification
name is always `LoRa`.  Parameters contains field `data` which is the data that was received.
Example:
```json
{
  "data": {
           "A1":1.63,
           "A0":1.77,
           "A3":1.33,
           "A2":1.48,
           "A5":0.64,
           "A4":1.15
  }
}
```
If LoRa data is a json it will be json object in this field. If LoRa data is a string or raw data it
will be string object in this field. Any non pritable character, it will be escaped with `\\x00`
sequence where `00` is hex code of char. For example newline char `\\x0a`.

To send data to LoRa, send a command to dateway device with `LoRa` name(case
insensetive) and `data` field in the parameters. It can be json object or string which will be
sent as bytes to radio. Any non pritable charactes should be escaped with `\\x00` sequence
where `00` is hex code of char.

# Sample LoRa device
There is a simple Arduino based(with LoRa hat) devices sample. This sample can be used for
test of demo purpose. See details [here](./lora-demo-device).

# Building from sources
To build firmwares and/or flash it separatly use [Arduino IDE](https://www.arduino.cc/en/Main/Software).
More deatiled description about operating Dragino gateway is aviliable [here](http://www.dragino.com/downloads/downloads/UserManual/LG01_LoRa_Gateway_User_Manual.pdf).
To generate release tarball:
- build [lora-gateway-firmware](./lora-gateway-firmware) with Arduino IDE(Sketch -> Export
compiled Binary)
- run `gen_release.sh` script
Tarball will be created in repo root directory.

# License
Apache License, Version 2.0. See [LICENSE](./LICENSE) file
