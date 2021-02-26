import board

if hasattr(board,"NEOPIXEL"):
	"""
	For a board that has a neopixel (eg: Feather NRF52840 Express)
	"""
	import neopixel
	status_led = neopixel.NeoPixel(board.NEOPIXEL, 1)
elif hasattr(board,"APA102_SCK"):
	"""
	For a board that has a APA102 (eg: UnexpectedMaker Feather S2)
	"""
	import adafruit_dotstar
	status_led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
else:
	raise OSError("No hardware pixel identified, please define some")

if hasattr(board,'LDO2'):
	"""
	Enable LDO2 on the Feather S2 so we can use the status LED
	"""
	from digitalio import DigitalInOut, Direction
	ldo2 = DigitalInOut(board.LDO2)
	ldo2.direction = Direction.OUTPUT
	ldo2.value = True
