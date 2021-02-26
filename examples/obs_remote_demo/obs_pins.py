import board

if hasattr(board,"NEOPIXEL"):
	# for a board that has a neopixel (eg: Feather NRF52840 Express)
	import neopixel
	hardware_pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
elif hasattr(board,"APA102_SCK"):
	# for a board that has a APA102 (eg: UnexpectedMaker Feather S2)
	import adafruit_dotstar
	hardware_pixels = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
else:
	raise OSError("No hardware pixel identified, please define some")

### Example using a 8-pixels RGBW neopixel stick
# from neopixel import NeoPixel
# hardware_pixels = NeoPixel(board.IO36, 8, bpp=4)

if hasattr(board,"IO9"):
	# UnexpectedMaker Feather S2
	button_twitch = board.IO7
	button_record = board.IO1
	button_buffer = board.IO33
elif hasattr(board,"D9"):
	# Feather NRF52840 Express
	button_twitch = board.D9
	button_record = board.D10
	button_buffer = board.D6
