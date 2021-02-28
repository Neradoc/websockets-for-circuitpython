import board
import os

if hasattr(board,"NEOPIXEL"):
	"""
	For a board that has a neopixel (eg: Feather NRF52840 Express)
	Also use the four pixels on the MagTag
	"""
	NPIXELS = 1
	if os.uname().machine.lower().find("magtag"):
		NPIXELS = 4
	import neopixel
	status_led = neopixel.NeoPixel(board.NEOPIXEL, NPIXELS)
elif hasattr(board,"APA102_SCK"):
	"""
	For a board that has a APA102 (eg: UnexpectedMaker Feather S2)
	"""
	NPIXELS = 1
	import adafruit_dotstar
	status_led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, NPIXELS)
else:
	raise OSError("No hardware pixel identified, please define some")

if hasattr(board,'LDO2'):
	"""
	Enable LDO2 on the Feather S2 so we can use the status LED
	"""
	from digitalio import DigitalInOut, Direction
	ldo2 = DigitalInOut(board.LDO2)
	ldo2.switch_to_output()
	ldo2.value = True

if hasattr(board,"NEOPIXEL_POWER"):
	"""
	On the MagTag, bring down NEOPIXEL_POWER
	"""
	from digitalio import DigitalInOut, Direction
	neopower = DigitalInOut(board.NEOPIXEL_POWER)
	neopower.switch_to_output()
	neopower.value = False
