/*
 * Copyright (C) 2017 DataArt
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <Console.h>
#include <Process.h>
#include <SPI.h>
#include <LoRa.h>

const uint32_t default_frequency = 868000000; // Frequency in Hz
int ledPin = A2;
Process deviceHive;
const char prefix_data[] = "data:";
const char prefix_frequency[] = "freq:";

void setup() {
  pinMode(ledPin, OUTPUT);
  Bridge.begin(115200);
  Console.begin();
  // while (!Console);

  Console.println("LoRa gateway firmware");

  if (!LoRa.begin(default_frequency)) {
    Console.println("Failed to LoRa.begin()");
    while (1);
  }

  deviceHive.runShellCommandAsynchronously("python /opt/devicehive/gateway.py daemon");
}

void loop() {
  char data[256 + sizeof(prefix_data)];
  unsigned int pos;
  // try to parse packet and send to DeviceHive
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    digitalWrite(ledPin, HIGH);
    Console.print("Received packet '");

    deviceHive.print(prefix_data);
    // read packet
    while (LoRa.available()) {
      char c = (char)LoRa.read();
      if (31 < c && c < 127) {
        deviceHive.write(c);
        Console.print(c);
      } else {
        snprintf(data, sizeof(data), "\\x%x", c);
        pos = 0;
        while (data[pos]) {
          deviceHive.write(data[pos]);
          Console.print(data[pos]);
          pos++;
        }
      }
    }
    deviceHive.write('\n');
    deviceHive.flush();
    Console.println("'");

    digitalWrite(ledPin, LOW);
  }

  pos = 0;
  while (deviceHive.available()) {
    data[pos] = (char)deviceHive.read();
    pos++;
    if (pos > sizeof(data) - 2)
        break;
  }
  data[pos] = 0;
  if (pos > 0) {
    digitalWrite(ledPin, HIGH);
    Console.print("Got: '");
    Console.print(data);
    Console.println("'");
  }

  if (strncmp(data, prefix_data, sizeof(prefix_data) - 1) == 0) {
    Console.print("Sending ");
    Console.print(pos - sizeof(prefix_data) + 1);
    Console.println(" bytes to LoRa");
    LoRa.beginPacket();
    for (int i = sizeof(prefix_data) - 1; i < pos; i++) {
      LoRa.write(data[i]);
    }
    LoRa.endPacket();
  } else if (strncmp(data, prefix_frequency, sizeof(prefix_frequency) - 1) == 0) {
    long int f = strtol(&data[sizeof(prefix_frequency) - 1], 0, 0);
    if (f == 0) {
      Console.println("Bad frequency value, not changed");
    } else {
      Console.print("Set new LoRa frequency ");
      Console.print(f);
      Console.println(" Hz");
      LoRa.end();
      if (!LoRa.begin(f)) {
        Console.println("Failed to set new frequency");
        LoRa.begin(default_frequency);
      }
    }
  }
  digitalWrite(ledPin, LOW);
}

