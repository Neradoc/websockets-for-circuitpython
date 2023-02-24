from secrets import secrets


def connect_wifi():
    try:
        import wifi

        native_wifi = True
    except:
        native_wifi = False

    if native_wifi:
        """
        That's for native wifi.
        """
        import socketpool
        import ssl

        print("CONNECT WIFI")
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        socket = socketpool.SocketPool(wifi.radio)
        ssl_context = ssl.create_default_context()
        return (socket, ssl_context, None)

    else:
        """
        That's for an ESP32 wifi coprocessor (airlift breakouts and integrated).
        Change the pins to those that match your board.
        """
        import board
        import busio
        from digitalio import DigitalInOut
        from adafruit_esp32spi import adafruit_esp32spi

        if hasattr(board, "ESP_CS"):
            # If you are using a board with pre-defined ESP32 Pins:
            esp32_cs = DigitalInOut(board.ESP_CS)
            esp32_ready = DigitalInOut(board.ESP_BUSY)
            esp32_reset = DigitalInOut(board.ESP_RESET)
        else:
            # If you have an externally connected ESP32:
            esp32_cs = DigitalInOut(board.D13)  # CHANGE TO MATCH YOUR BOARD
            esp32_ready = DigitalInOut(board.D11)  # CHANGE TO MATCH YOUR BOARD
            esp32_reset = DigitalInOut(board.D12)  # CHANGE TO MATCH YOUR BOARD

        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

        print("CONNECT WIFI")
        while not esp.is_connected:
            try:
                esp.connect_AP(secrets["ssid"], secrets["password"])
            except RuntimeError as e:
                print("could not connect to AP, retrying: ", e)
                continue

        import adafruit_esp32spi.adafruit_esp32spi_socket as socket

        socket.set_interface(esp)
        return (socket, None, esp)

    return (None, None, None)
