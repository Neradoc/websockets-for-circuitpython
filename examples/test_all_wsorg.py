## set debug to False for future imports (removes logging)
# import micropython
# micropython.opt_level(1)

from connect_circuitpython import connect_wifi

socket, ssl_context, iface = connect_wifi()

from uwebsockets import Session

wsession = Session(socket, ssl=ssl_context, iface=iface)

message = "Repeat this"
urls = [
    "wss://echo.websocket.org",
    "ws://echo.websocket.org",
]

for url in urls:
    print(f"TESTING ECHO {url}")
    with wsession.client(url) as ws:
        print(f"SENDING:  <{message}>")
        ws.send(message)
        result = ws.recv()
        print(f"RECEIVED: <{result}>")
        if result == message:
            print("SUCCESS !!")
        else:
            print("OH NO IT WENT WRONG")
