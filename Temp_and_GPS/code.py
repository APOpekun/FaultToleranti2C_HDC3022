import microcontroller
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
import adafruit_max1704x # for the Battery Monitor
import adafruit_gps #reserved for GPS
#Reserved for SD card ReadWrite
# Initialize display
displayio.release_displays()

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

#initialize GPS 
# Connect UART rx to GPS module TX, and UART tx to GPS module RX.
tx = board.TX  # Use board.GP4 or other UART TX on Raspberry Pi Pico boards.
rx = board.RX  # Use board.GP5 or other UART RX on Raspberry Pi Pico boards.
uart = busio.UART(tx, rx, baudrate=9600, timeout=10)
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")


display_bus = I2CDisplayBus(i2c, device_address=0x3C)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 2

display = adafruit_displayio_sh1107.SH1107(
    display_bus,
    width=HEIGHT,
    height=WIDTH,
    rotation=90
)

#initialize the battery monitor
max17 = adafruit_max1704x.MAX17048(i2c)
print(
    "Found MAX1704x with chip version",
    hex(max17.chip_version),
    "and id",
    hex(max17.chip_id),
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
TempSens = [adafruit_mcp9808.MCP9808(i2c, address=0x18 + i) for i in range(8)]
#Confirm the sensors are responding.
for addr in range(0x18, 0x20):
    try:
        adafruit_mcp9808.MCP9808(i2c, address=addr)

        print("Found:", hex(addr))
    except Exception:
        print(Exception)
        print("Missing:", hex(addr))



for sensor in TempSens: #Set Resolutions to
    sensor.resolution = 3
    """
    Temperature Resolution in Celsius
    =======   ============   ==============
    Value     Resolution     Reading Time
    =======   ============   ==============
    0          0.5°C            30 ms
    1          0.25°C           65 ms
    2         0.125°C          130 ms
    3         0.0625°C         250 ms
    =======   ============   ==============
    """



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
    return temps

text = "T0: {:.2f} C".format(TempSens[0].temperature)

text_area = label.Label(
    terminalio.FONT,
    text=text,
    color=0xFFFFFF,
    x=0,
    y=10,
)
N = 0
last_time = time.monotonic()
while True:
    gps.update()
    current_time = time.monotonic()
    
    if current_time - last_time >= 1.0:
        last_time = current_time
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            
            addr_text = "Waiting\nfor\nfix..."
            print(addr_text)
            
            text_area = label.Label(terminalio.FONT, text=addr_text, color=0xFFFFFF, x=5, y=8)
            
            # Make the display context
            screen = displayio.Group()
            screen.append(text_area)
            display.root_group = screen
            continue
        
        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        print("=" * 40)  # Print a separator line.
        print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(  # noqa: UP032
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
                gps.timestamp_utc.tm_mday,  # struct_time object that holds
                gps.timestamp_utc.tm_year,  # the fix time.  Note you might
                gps.timestamp_utc.tm_hour,  # not get all data like year, day,
                gps.timestamp_utc.tm_min,  # month!
                gps.timestamp_utc.tm_sec,
            )
        )
        print(f"Latitude: {gps.latitude:.6f} degrees")
        print(f"Longitude: {gps.longitude:.6f} degrees")
        print(f"Precise Latitude: {gps.latitude_degrees} degs, {gps.latitude_minutes:2.4f} mins")
        print(f"Precise Longitude: {gps.longitude_degrees} degs, {gps.longitude_minutes:2.4f} mins")
        print(f"Fix quality: {gps.fix_quality}")
        
        temps = Aquire()
        battLVLs = [max17.cell_voltage,max17.cell_percent]
        print(f"Battery voltage: {battLVLs[0]:.2f} Volts")
        print(f"Battery state  : {battLVLs[1]:.1f} %")
        print("")
        
        # Make the display context
        screen = displayio.Group()
        for i, temp in enumerate(temps):
            addr_text = f"{temp:06.4f}"
            text_area = label.Label(terminalio.FONT, text=addr_text, color=0xFFFFFF, x=5, y=8+ i * 12)
            screen.append(text_area)
        screen.append(label.Label(terminalio.FONT, text=f"{battLVLs[0]:05.2f} V", color=0xFFFFFF, x=5, y=110))
        screen.append(label.Label(terminalio.FONT, text=f"{battLVLs[1]:05.2f} %", color=0xFFFFFF, x=5, y=122))
        display.root_group = screen
