# Import time (to sleep) and RPi.GPIO
import time
import RPi.GPIO as GPIO

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

# Set pixel count of the LED stripe
PIXEL_COUNT = 32

# Define BCM PIN numbers for switches
SWITCH1 = 19
SWITCH2 = 26

# Define colors for stepper
COLOR1   = [0, 255, 0]
COLOR2   = [255, 0, 0]
NEWCOLOR = list(COLOR1)
OLDCOLOR = list(COLOR1)
STEPS    = 8
NEWSTEP  = 0
OLDSTEP  = 0



print("--------------------------------------------------")
print("GPIO CONFIGURATION")
print("--------------------------------------------------")

print("set GPIO numbering mode to BCM")
GPIO.setmode(GPIO.BCM)
if (GPIO.getmode() == GPIO.BCM):
	print("GPIO numbering mode is BCM")
if (GPIO.getmode() == GPIO.BOARD):
	print("GPIO numbering mode is BOARD")

print("set GPIO {} to input mode".format(SWITCH1))
print("activate PULL UP resistor on GPIO {}".format(SWITCH1))
GPIO.setup(SWITCH1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#print("GPIO {} is {}".format(SWITCH1, GPIO.input(SWITCH1)))

print("set GPIO {} to input mode".format(SWITCH2))
print("activate PULL UP resistor on GPIO {}".format(SWITCH2))
GPIO.setup(SWITCH2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
#print("GPIO {} is {}".format(SWITCH2, GPIO.input(SWITCH2)))



print("--------------------------------------------------")
print("Adafruit WS2801 CONFIGURATION")
print("--------------------------------------------------")

print("pixel count set to", PIXEL_COUNT)

# Specify a software SPI connection for Raspberry Pi on the following pins:
#~ PIXEL_CLOCK = 11
#~ PIXEL_DOUT  = 10
#~ pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, clk=PIXEL_CLOCK, do=PIXEL_DOUT)

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
print("hardware SPI connection activated")



#~ print("--------------------------------------------------")
#~ print("DEFINE FUNCTIONS")
#~ print("--------------------------------------------------")

# This function takes a number from 0..255
# and converts it into a RGB color.
def color(pos):
	if 0*85 <= pos < 1*85:
		cval = (pos - 0*85) * 3
		return Adafruit_WS2801.RGB_to_color(cval, 255 - cval, 0)

	if 1*85 <= pos < 2*85:
		cval = (pos - 1*85) * 3
		return Adafruit_WS2801.RGB_to_color(255 - cval, 0, cval)

	if 2*85 <= pos < 3*85:
		cval = (pos - 2*85) * 3
		return Adafruit_WS2801.RGB_to_color(0, cval, 255 - cval)



# Light up all LEDs one after the other in rainbow colors
def rainbow_startup(pixels, wait = 0.1):
	for i in range(pixels.count()):
		pos = (i * 256 // pixels.count()) % 256
		pixels.set_pixel(i, color(pos)
		pixels.show()
		if wait > 0:
			time.sleep(wait)



def set_step(step):
	global COLOR1
	global COLOR2
	global NEWCOLOR
	global OLDCOLOR
	global STEPS

	# COLOR
	OLDCOLOR = list(NEWCOLOR)
	for i in range(3):
		NEWCOLOR[i] = COLOR1[i] + step * ((COLOR2[i] - COLOR1[i]) // STEPS)
		NEWCOLOR[i] = min(NEWCOLOR[i], 255)
		NEWCOLOR[i] = max(NEWCOLOR[i], 0)

	# print the colors
	print("COLOR1 =", COLOR1)
	print("COLOR2 =", COLOR2)
	print("OLDCOLOR =", OLDCOLOR)
	print("NEWCOLOR =", NEWCOLOR)

	# Distribute new color
	for i in range(pixels.count()):
		# 0..i
		for j in range(0, i):
			pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color(NEWCOLOR[0], NEWCOLOR[1], NEWCOLOR[2]))
		# i
		pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(255, 255, 255))
		# i+1 ... pixels
		#~ for j in range(i+1, pixels.count()):
			#~ pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color(OLDCOLOR[0], OLDCOLOR[1], OLDCOLOR[2]))
		pixels.show()
		time.sleep(0.01)

	# set the last pixel
	pixels.set_pixel(pixels.count()-1, Adafruit_WS2801.RGB_to_color(NEWCOLOR[0], NEWCOLOR[1], NEWCOLOR[2]))
	pixels.show()




def button_pressed(channel):
	print("--------------------------------------------------")
	print("callback for edge detect on GPIO {}".format(channel))

	global STEPS
	global NEWSTEP
	global OLDSTEP

	# STEP
	OLDSTEP = NEWSTEP
	if (channel > 20):
		NEWSTEP = OLDSTEP - 1
	else:
		NEWSTEP = OLDSTEP + 1
	NEWSTEP = min(NEWSTEP, STEPS)
	NEWSTEP = max(NEWSTEP, 0)

	# print the steps
	print("OLDSTEP =", OLDSTEP)
	print("NEWSTEP =", NEWSTEP)

	if (OLDSTEP == NEWSTEP):
		return

	set_step(NEWSTEP)





if __name__ == "__main__":

	print("--------------------------------------------------")
	print("START MAIN PROGRAM")
	print("--------------------------------------------------")

	print("clear all pixels to turn them off")
	pixels.clear()
	pixels.show()

	print("set edge detect callback function for GPIO {}".format(SWITCH1))
	GPIO.add_event_detect(SWITCH1, GPIO.FALLING, callback=button_pressed, bouncetime=500)

	print("set edge detect callback function for GPIO {}".format(SWITCH2))
	GPIO.add_event_detect(SWITCH2, GPIO.FALLING, callback=button_pressed, bouncetime=500)



	rainbow_cycle_successive(pixels, wait=0.1)

	NEWSTEP = STEPS//2
	set_step(NEWSTEP)



	while (1):
		#do nothing
		time.sleep(1)



	print("clear all pixels to turn them off")
	pixels.clear()
	pixels.show()

	print("cleanup, i.e. reset all channels to input")
	GPIO.cleanup()
