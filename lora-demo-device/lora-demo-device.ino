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

#include <SPI.h>
#include <LoRa.h>

const uint32_t frequency = 868000000; // Frequency in Hz
const int ledPin = 7;
const unsigned long INTERVAL_MS = 5000;
unsigned long last_sent;

void setup() 
{
  Serial.begin(9600);
  while (!Serial);
  Serial.println("DeviceHive LoRa demo device");
  if(LoRa.begin(frequency)== 0) {
    Serial.println("Failed to LoRa.begin()");
  };
  LoRa.setTxPower(13);
  pinMode(ledPin, OUTPUT);
  last_sent = millis() - INTERVAL_MS;
}

void loop()
{
  char data[255];
  if(millis() - last_sent > INTERVAL_MS) {
    last_sent = millis();
    Serial.print("Sending demo data: ");
    char values[6][6];
    for(int i = 0; i < 6; i++) {
      float v = analogRead(i) * (5.0 / 1023.0);
      dtostrf(v, 4, 2, (char*)&values[i]);
    }
    int l= snprintf(data, sizeof(data), 
                    "{\"A0\":%s, \"A1\":%s, \"A2\":%s, \"A3\":%s, \"A4\":%s, \"A5\":%s}",
                    values[0], values[1], values[2], values[3], values[4], values[5]);
    Serial.println(data);
    if(LoRa.beginPacket() == 0) {
      Serial.println("Failed to LoRa.beginPacket()");
      return;
    }
    if(LoRa.write(data, l) == 0) {
      Serial.println("Failed to LoRa.beginPacket()");
      return;
    }
    if(LoRa.endPacket() == 0) {
      Serial.println("Failed to LoRa.beginPacket()");
      return;
    }
  }

  // try to read data
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    int pos = 0;
    Serial.print("Received packet '");

    while (LoRa.available()) {
      char c = (char)LoRa.read();
      Serial.print(c);
      data[pos] = c;
      pos++;
      if(pos > sizeof(data) - 2)
        break;
    }
    Serial.println("'");
    data[pos] = 0;
    if(strstr(data, "led/on")) {
      Serial.println("Turn the LED on");
      digitalWrite(ledPin, HIGH);
    } else if(strstr(data, "led/off")) {
      Serial.println("Turn the LED off");
      digitalWrite(ledPin, LOW);
    }
  }
}

