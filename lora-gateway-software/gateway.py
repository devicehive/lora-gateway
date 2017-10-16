#!/usr/bin/env python

# Copyright (C) 2017 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import os
import subprocess
import daemon

# while True:
#     s = raw_input()
#     with open('/root/log.txt', 'a') as f:
#         f.write(s+'\r\n')
#     time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",
                        help="select run mode, can be 'install' or 'daemon'."
                             "Install mode just flashes firmware to chip, "
                             "daemon mode runs cloud connector from the "
                             "firmware side, do not call it manually.")
    args = parser.parse_args()
    if args.mode == "install":
        print("Flashing MCU with avrdude...")
        subprocess.call(["run-avrdude",
                         os.path.join(os.path.dirname(
                                os.path.realpath(__file__)),
                            "lora-gateway-firmware.ino.arduino_standard.hex"),
                         "-v", "-patmega328p"])
    elif args.mode == "daemon":
        logging.StreamHandler(stream=None)
        daemon.run()
    else:
        print("Unknown mode. Use -h for help.")


if __name__ == '__main__':
    main()
