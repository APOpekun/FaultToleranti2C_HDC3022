import time
import board
import digitalio
import displayio
import busio

from i2cdisplaybus import I2CDisplayBus # to connect to the SH1107 Display
import adafruit_displayio_sh1107
from adafruit_display_text import label
import terminalio
import adafruit_mcp9808 #for the Temperature Sensor
#reserved for GPS
#Reserved for SD card ReadWrite

displayio.release_displays()

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize display
display_bus = I2CDisplayBus(i2c, device_address=0x3C)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(
    display_bus, width=WIDTH, height=HEIGHT, rotation=0
)

#initialize the sensors
##Accepted range
TEMP_MIN = -40.0
TEMP_MAX = 125.0
# Fall back
ERROR = -100.00
#Sensor Health array 1=good, 0=bad
sensor_health = [1] * 8

# Initialize 8 MCP9808 sensors
TempSens = [
    adafruit_mcp9808.MCP9808(i2c, address=0x18 + i)
    for i in range(8)
]

# Make the display context
splash = displayio.Group()
display.root_group = splash

# Define button inputs
button_a = digitalio.DigitalInOut(board.D9)
button_b = digitalio.DigitalInOut(board.D6)
button_c = digitalio.DigitalInOut(board.D5)
for b in (button_a, button_b, button_c):
    b.switch_to_input(pull=digitalio.Pull.UP)

# Button edge tracking (pull-ups: True = idle, False = pressed)
last_a = button_a.value
last_b = button_b.value
last_c = button_c.value

# Function to clear the screen
def black_screen():
    for i in range(len(splash)):
        try:
            splash.pop()
        except:
            pass
            
# Define states
STATE_MAIN_MENU = 0 # Start Here


STATE_AQUIRE = 1 
#use a loop to query each sensor through safe_read(sensor) that returns (temp) with fallback values

def safe_read(sensor):
    try:
        t = sensor.temperature
        if (t < TEMP_MIN) or (t > TEMP_MAX):
            return ERROR, 0
        return t, 1
    except Exception:
        return ERROR, 0
        
#not sure which is faster on Time return GPS or RTC
#if RTC is faster then update RTC from GPS every ... 5 or 10 minutes? at the point where drift gets too much
def Aquire():
    temps = []
    timestamp1 = "Day Mon N HH:MM:SS.ssss YYYY" #from GPS or RTC Not available yet
    for i, sensor in enumerate(TempSens):
        t, ok = safe_read(sensor)
        sensor_health[i] = ok
        temps.append(t)
    timestamp2 = "Day Mon N HH:MM:SS.ssss YYYY" #from GPS or RTC Not available yet
    return timestamp1,temps,timestamp2

while True:
    print(Aquire())
    time.sleep(5)