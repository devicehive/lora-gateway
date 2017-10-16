#!/bin/bash

set -e

DIR=$(realpath $(dirname $0))
BUILD=$DIR/build
mkdir -p $BUILD
cp $DIR/lora-gateway-software/*.py $BUILD
cp $DIR/lora-gateway-firmware/lora-gateway-firmware.ino.arduino_standard.hex $BUILD
(cd $BUILD && tar -czf ../gateway.tar.gz *)
