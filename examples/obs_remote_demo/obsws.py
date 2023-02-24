# SPDX-FileCopyrightText: Copyright (c) 2017 Guillaume "Elektordi" Genty
# SPDX-FileCopyrightText: Copyright (c) 2022 Neradoc
# SPDX-License-Identifier: MIT

import adafruit_hashlib as hashlib
import binascii
import json
from uwebsockets import Session
from connect_circuitpython import connect_wifi


class ConnectionFailure(BaseException):
    pass


def base64(input):
    tmp = binascii.b2a_base64(input)
    return tmp[:-1]


class obsws:
    def __init__(self, host=None, port=4444, password=""):
        self.id = 0
        # self.thread_recv = None
        # self.eventmanager = EventManager()
        # self.answers = {}
        self.host = host
        self.port = port
        self.password = password
        self.ws = None

    def connect(self):
        URL = "ws://{}:{}".format(self.host, self.port)
        socket, ssl_context, iface = connect_wifi()
        session = Session(socket, ssl=ssl_context, iface=iface)
        self.ws = session.client(URL)
        self._auth(self.password)

    def _auth(self, password):
        self.id += 1
        auth_payload = {"request-type": "GetAuthRequired", "message-id": str(self.id)}
        self.ws.send(json.dumps(auth_payload))
        result = json.loads(self.ws.recv())
        print("obsws result:", result)

        if result["authRequired"]:
            secret = base64(
                hashlib.sha256((password + result["salt"]).encode("utf-8")).digest()
            )
            auth = base64(
                hashlib.sha256(secret + result["challenge"].encode("utf-8")).digest()
            ).decode("utf-8")

            self.id += 1
            auth_payload = {
                "request-type": "Authenticate",
                "message-id": str(self.id),
                "auth": auth,
            }
            self.ws.send(json.dumps(auth_payload))
            result = json.loads(self.ws.recv())
            if result["status"] != "ok":
                raise ConnectionFailure(result["error"])

    def recv(self):
        self.ws.settimeout(0.1)
        try:
            rec = self.ws.recv()
            if rec.strip() != "":
                result = json.loads(rec)
            else:
                result = {}
            return result
        except OSError as err:
            # timeout
            if err.args[0] == 110 or err.args[0] == 116:
                return None
            else:
                raise err

    def send(self, payload):
        self.id += 1
        payload["message-id"] = str(self.id)
        self.ws.settimeout(None)
        self.ws.send(json.dumps(payload))
        # NOTE: il envoie "replay starting" "replay started" first
        # donc il ne faut pas attendre de recv() un status ok
        # result = json.loads(self.ws.recv())
        # return result
        return self.id
