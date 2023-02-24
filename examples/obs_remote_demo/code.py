# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
# SPDX-License-Identifier: MIT

from digitalio import DigitalInOut, Pull
import gamepad
import gc
import time
from secrets import secrets

from connect_circuitpython import connect_wifi
import obs_pins as pins
from obsws import obsws

# OBS connection info
url = secrets["obs_url"]
password = secrets["obs_password"]

# Reset all
def reset():
    import microcontroller

    microcontroller.reset()


################################################################
# neopixels and colors
################################################################

from obs_colors import *


class MyPix:
    def __init__(self, pixel):
        self._pixel = pixel

    def __getattr__(self, attr):
        if (self._pixel, attr):
            return getattr(self._pixel, attr)

    def set_pattern(self, values):
        for pos, val in enumerate(values):
            if val != None:
                self._pixel[pos] = val
        self._pixel.show()


# RGBW: bpp = 4
pixels_strip = MyPix(pins.hardware_pixels)
pixels_strip.brightness = BRIGHTNESS
pixels_strip.fill(STARTUP)
pixels_strip.show()

# passage en mode erreur
def dieInError():
    print("DEAD IN ERROR")
    pixels_strip.fill((255, 0, 0))
    pixels_strip.show()


################################################################
# blink the statuses
# sets the neopixels colors to each status one after the other
# is a status has a pixel as None, don't change it
# so if multiple pixels, they be made to stay a single color
# by using each for one state
################################################################

swirl_interval = const(2)


class StatusColor(dict):
    def __init__(self):
        self.patterns = {}
        self.pos = 0
        self.t0 = time.monotonic()

    def append(self, key, pattern):
        self.patterns[key] = pattern
        self.show_all()

    def remove(self, key):
        if key in self.patterns:
            del self.patterns[key]
            self.show_all()

    def show_all(self):
        if len(self.patterns) > 0:
            colors = [OFF] * pixels_strip.n
            for status, color_pattern in self.patterns.items():
                for index, color in enumerate(color_pattern):
                    if color is not None:
                        colors[index] = color
            pixels_strip.set_pattern(colors)
        else:
            pixels_strip.set_pattern(ALL_OFF)
        self.t0 = time.monotonic()

    def update_swirl(self):
        if len(self.patterns) == 0:
            pixels_strip.set_pattern(ALL_OFF)
        else:
            self.pos = (self.pos + 1) % len(self.patterns)
            current = sorted(self.patterns.keys())[self.pos]
            pixels_strip.set_pattern(self.patterns[current])

    def cycle_call(self):
        t1 = time.monotonic()
        if t1 - self.t0 > swirl_interval:
            self.t0 = t1
            self.update_swirl()


status_colors = StatusColor()

################################################################
# buttons ! who doesn't like buttons ?
################################################################


class Button:
    def __init__(self, pin, pull):
        self.pin = DigitalInOut(pin)
        if pull == "UP":
            self.pin.switch_to_input(pull=Pull.UP)
            self.pull = True
        elif pull == "DOWN":
            self.pin.switch_to_input(pull=Pull.DOWN)
            self.pull = False
        else:
            raise (ValueError("Button: pull must be UP or DOWN"))
        self.wasOn = False

    @property
    def on(self):
        return self.pin.value != self.pull

    @property
    def pressed(self):
        if self.on and not self.wasOn:
            self.wasOn = True
            return True
        elif not self.on and self.wasOn:
            self.wasOn = False
        return False


button_twitch = Button(pins.button_twitch, "UP")
button_record = Button(pins.button_record, "UP")
button_buffer = Button(pins.button_buffer, "UP")

################################################################
# event manager to register and react to messages from OBS
################################################################

# Events System
reactions = []
updates = []


class React:
    def __init__(self, messageId, action):
        self.id = str(messageId)
        self.action = action


class Update:
    def __init__(self, updateType, action):
        self.type = updateType
        self.action = action


################################################################
# manage the buffer record button/feature
################################################################


def buffer_on(message=None):
    pass
    # status_colors["buffer"] = BUFFER


def buffer_off(message=None):
    pass
    # del status_colors["buffer"]


def buffer_start():
    global obs
    id = obs.send({"request-type": "StartReplayBuffer"})
    reactions.insert(0, React(id, buffer_on))


################################################################
# manage the record and stream actions
################################################################
statusRecord = False
statusStream = False


def status_got(message=None):
    global statusStream, statusRecord
    statusStream = message["streaming"]
    statusRecord = message["recording"]
    if statusStream:
        status_colors.append("stream", STREAM)
    elif "stream" in status_colors:
        status_colors.remove("stream")
    if statusRecord:
        status_colors.append("record", RECORD)
    elif "record" in status_colors:
        status_colors.remove("record")


def get_status():
    global obs, reactions
    id = obs.send({"request-type": "GetStreamingStatus"})
    print("GetStreamingStatus", id)
    reactions.insert(0, React(id, status_got))


################################################################
# helper functions for the loop
################################################################

# ACT ON MESSAGE
def act_on_message(rec):
    global reactions
    for re in reversed(reactions):
        if re.id == rec["message-id"]:
            re.action(rec)
            reactions.remove(re)


# ACT ON UPDATE
def act_on_update(rec):
    global statusStream, statusRecord, status_colors
    for up in updates:
        if up.type == rec["update-type"]:
            up.action(rec)
    if rec["update-type"] == "StreamStarted":
        statusStream = True
        status_colors.append("stream", STREAM)
    elif rec["update-type"] == "StreamStopped":
        statusStream = False
        status_colors.remove("stream")
    elif rec["update-type"] == "RecordingStarted":
        statusRecord = True
        status_colors.append("record", RECORD)
    elif rec["update-type"] == "RecordingStopped":
        statusRecord = False
        status_colors.remove("record")
    elif rec["update-type"] == "Exiting":
        # TODO: do something about the disconnection
        print("DECO -- DO SOMETHING")


# ACT ON BUTTONS
def act_on_buttons():
    if button_twitch.pressed:
        print("Button Stream")
        if statusStream:
            id = obs.send({"request-type": "StopStreaming"})
        else:
            id = obs.send({"request-type": "StartStreaming"})

    if button_record.pressed:
        print("Button Record")
        if statusRecord:
            id = obs.send({"request-type": "StopRecording"})
        else:
            id = obs.send({"request-type": "StartRecording"})

    if button_buffer.pressed:
        print("Button Buffer")
        id = obs.send({"request-type": "SaveReplayBuffer"})


################################################################
#
# the "main" loop pat
#
################################################################

# connect to OBS (OR DIE)
obs = None


def connect():
    global obs
    try:
        obs = obsws(url, 4444, password)
        obs.connect()
    except Exception as Ex:
        dieInError()
        print("Exception")
        print(Ex)
        raise Ex


# register buffer updates
updates.append(Update("ReplayStopped", buffer_off))
updates.append(Update("ReplayStarted", buffer_on))

# the OBS loop
def obs_reading_loop():
    global obs
    try:
        while True:
            gc.collect()
            rec = obs.recv()
            if rec:
                print("@recv", rec)
                if "message-id" in rec:
                    act_on_message(rec)
                if "update-type" in rec:
                    act_on_update(rec)
                gc.collect()
                # print("MEM",gc.mem_free())
            act_on_buttons()
            time.sleep(0.01)
            status_colors.cycle_call()
            #
    except Exception as Ex:
        dieInError()
        print("Exception")
        print(Ex)
        raise Ex
        # reset()


# the global while loop for connection
while True:
    try:
        connect()
        if obs != None:
            # start the buffer, get the status
            buffer_start()
            get_status()
            gc.collect()
            # do the loop
            obs_reading_loop()
    except Exception as Ex:
        obs = None
        dieInError()
        print("Exception")
        print(Ex)
        if Ex.args[0] == 104 or Ex.args[0] == 103:  # ECONNRESET / ECONNABORTED
            print("CONNECTION FAILED - SLEEP AND RETRY")
            time.sleep(10)
        else:
            raise Ex

print("FIN")
dieInError()
