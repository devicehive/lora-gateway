# !/usr/bin/env python
# -*- coding: utf-8 -*-

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

import json
import threading
import os
import uuid
import sys
from cgi import parse_header, parse_multipart
from urlparse import parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from devicehive import Handler
from devicehive import DeviceHive
from devicehive import api_response

FILE_NAME = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                         "config.json")

HEAD = "<head><title>DeviceHive LoRa gateway</title>" \
       "<meta name = 'viewport' content = 'width=device-width," \
       "initial-scale=1.0'>" \
       "<style>input[type='text'], input[type='password'] { width: 100%}" \
       "</style></head>"

NOTIFICATION_NAME = "LoRa"
COMMAND_NAME = "lora"
DATA_PREFIX = "data:"
FREQUENCY_PREFIX = "freq:"


class DeviceHiveHandler(Handler):
    def __init__(self, api, deviceid, receive_cb, state):
        super(DeviceHiveHandler, self).__init__(api)
        self._device = None
        self._deviceid = deviceid
        self._receive_cb = receive_cb
        self._state = state

    def handle_connect(self):
        self._device = self.api.put_device(self._deviceid)
        self._device.subscribe_insert_commands()
        self._state.status = "Connected"
        self._state.is_connected = True

    def handle_command_insert(self, command):
        if command.command.lower() != COMMAND_NAME:
            command.status = "Unknown command"
        elif "data" in command.parameters:
            self._receive_cb(command.parameters["data"])
            command.status = "Ok"
        else:
            command.status = "Error, no data"
        command.save()

    def send_notification(self, data, rssi):
        if self._device is not None:
            try:
                obj = {"data": json.loads(data)}
            except ValueError:
                obj = {"data": data}
            if rssi is not None:
                obj["rssi"] = rssi
            self._device.send_notification(NOTIFICATION_NAME, obj)


class State:
    class Config:
        def __init__(self):
            self.url = 'http://playground.devicehive.com/api/rest'
            self.token = ''
            self.deviceid = 'lora-gateway-' + str(uuid.uuid4())[:8]
            self.frequency = 868000000

    def __init__(self, updated_cb):
        self.__callback = updated_cb
        self.status = "Not configured"
        self.is_connected = False
        self.cfg = self.Config()

    def save(self):
        try:
            with open(FILE_NAME, "wb") as f:
                json.dump(self.cfg.__dict__, f)
        except IOError:
            return False
        self.__callback()
        return True

    def load(self):
        try:
            with open(FILE_NAME, "rb") as f:
                tmp_dict = json.load(f)
                self.cfg.__dict__.clear()
                self.cfg.__dict__.update(tmp_dict)
        except IOError:
            return False
        self.__callback()
        return True


class ConfigHandler(BaseHTTPRequestHandler):
    def __init__(self, state, *args):
        self.state = state
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        d = None
        if self.path == '/' or self.path == '/index.html':
            d = "<html>" + HEAD
            d += "<body>Status: " + self.state.status + "<br>"
            d += "<form action='/' method='POST'><br>DeviceHive URL:<br>"
            d += "<input type='text' name='url' value='" + self.state.cfg.url \
                 + "'><br>"
            d += "<br>DeviceHive RefreshToken:<br>"
            d += "<input type='password' name='token' value='" \
                 + self.state.cfg.token + "'><br>"
            d += "<br>DeviceHive DeviceID:<br>"
            d += "<input type='text' name='deviceid' value='" \
                 + self.state.cfg.deviceid + "'><br>"
            d += "<br>LoRa Frequency, Hz:<br>"
            d += "<input type='text' name='frequency' value='" \
                 + str(self.state.cfg.frequency) + "'><br>"
            d += "<br><input type='submit' value='Save'>"
            d += "</form></body></html>"
        if d is not None:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(d)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        postvars = {}
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
        err = False
        try:
            url = postvars.get("url")[0]
            token = postvars.get("token")[0]
            deviceid = postvars.get("deviceid")[0]
            frequency = int(postvars.get("frequency")[0])
            self.state.cfg.url = url
            self.state.cfg.token = token
            self.state.cfg.deviceid = deviceid
            self.state.cfg.frequency = frequency
        except TypeError:
            err = True
        if not self.state.save():
            err = True
        if err:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html>" + HEAD)
            self.wfile.write("<body><font color=red>Error. Failed to save.")
            self.wfile.write("<br><a href='/'>Go back</a>")
            self.wfile.write("</font></body></html>")
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html>" + HEAD)
            self.wfile.write("<body><font color=green>Successfully saved.")
            self.wfile.write("<br><a href='/'>Go back</a>")
            self.wfile.write("</font></body></html>")

    def log_message(self, fmt, *args):
        return


class Daemon(HTTPServer):
    def __init__(self, data_callback, config_callback):
        self.__data_callback = data_callback
        self.__config_callback = config_callback
        self._devicehive_thread = None
        self.devicehive = None
        self.state = State(self.update_config)
        self.state.load()

        def handler(*args):
            ConfigHandler(self.state, *args)
        HTTPServer.__init__(self, ('0.0.0.0', 8000), handler)
        self._loop_thread = threading.Thread(target=self._httpd_loop)
        self._loop_thread.setDaemon(True)
        self._loop_thread.start()

    def _devicehive_loop(self):
        self.state.status = "Connecting..."
        try:
            self.devicehive.connect(self.state.cfg.url,
                                    refresh_token=self.state.cfg.token)
        except api_response.ApiResponseError as e:
            sys.stderr.write(' '.join(e) + '\n')
        self.devicehive = None
        self.state.status = "Disconnected"

    def update_config(self):
        if self.devicehive is not None:
            self.state.is_connected = False
            self.devicehive.handler.api.disconnect()
        self.devicehive = DeviceHive(DeviceHiveHandler,
                                     self.state.cfg.deviceid,
                                     self.__data_callback, self.state)
        self._devicehive_thread = threading.Thread(
            target=self._devicehive_loop)
        self._devicehive_thread.setDaemon(True)
        self._devicehive_thread.start()
        self.__config_callback(self.state.cfg)

    def _httpd_loop(self):
        self.serve_forever()

    def close(self):
        self.shutdown()

    def send(self, data, rssi):
        if self.state.is_connected and self.devicehive is not None \
                and self.devicehive.handler is not None:
            self.devicehive.handler.send_notification(data, rssi)


def decode_string(s):
    return s.decode("string_escape")


def receive_callback(data):
    if isinstance(data, dict):
        sys.stdout.write(DATA_PREFIX + decode_string(json.dumps(data)))
    else:
        sys.stdout.write(DATA_PREFIX + decode_string(data))
    sys.stdout.flush()


def config_cb(data):
    sys.stdout.write(FREQUENCY_PREFIX + str(data.frequency))
    sys.stdout.flush()


def run():
    d = Daemon(receive_callback, config_cb)
    while True:
        s = raw_input()
        if s[:len(DATA_PREFIX)] == DATA_PREFIX:
            rssi, data = s[len(DATA_PREFIX):].split('|', 1)
            d.send(data, float(rssi))
