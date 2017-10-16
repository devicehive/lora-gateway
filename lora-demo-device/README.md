# DeviceHive LoRa demo device
This device sends analog pins state every 5 seconds. If it receives data which
contains `led/on` or `led/off` it turn on/off on pin 7(13 pin with connected on board LED is
used by SPI's CLK). This sample can be run with Arduino Uno and [Dragino Lora Shield](http://www.dragino.com/products/module/item/102-lora-shield.html).
Use Arduino IDE to flash it.

# Dependencies
This demo project uses [Arduino LoRa](https://github.com/sandeepmistry/arduino-LoRa).
Make sure that this library is installed in your Arduino IDE, it's available in Arduino IDE Library
Manager.
