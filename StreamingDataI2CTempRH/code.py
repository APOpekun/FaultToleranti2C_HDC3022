import time
import board
import digitalio
import displayio
import busio
from adafruit_displayio_sh1107 import SH1107
import adafruit_hdc302x
import terminalio
from adafruit_display_text import label

# Release any resources currently in use for the displays
displayio.release_displays()

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize display
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
WIDTH = 64
HEIGHT = 128
display = SH1107(display_bus, width=HEIGHT, height=WIDTH, rotation=0)

# Make the display context
splash = displayio.Group()
display.root_group = splash

#define the 4 sensors
sensor0 = adafruit_hdc302x.HDC302x(i2c, address=0x44)
sensor1 = adafruit_hdc302x.HDC302x(i2c, address=0x45)
sensor2 = adafruit_hdc302x.HDC302x(i2c, address=0x46)
sensor3 = adafruit_hdc302x.HDC302x(i2c, address=0x47)

# Define button inputs
button_a = digitalio.DigitalInOut(board.D9)
button_b = digitalio.DigitalInOut(board.D6)
button_c = digitalio.DigitalInOut(board.D5)
button_a.switch_to_input(pull=digitalio.Pull.UP)
button_b.switch_to_input(pull=digitalio.Pull.UP)
button_c.switch_to_input(pull=digitalio.Pull.UP)

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

# Load the splash screen image
odb = displayio.OnDiskBitmap('/thesis_splash_128_64.bmp')
face = displayio.TileGrid(odb, pixel_shader=odb.pixel_shader)
splash.append(face)

# Wait for the image to load
display.refresh()
time.sleep(1)  # Simulate reading time

#This code wil capture data from the sensors and send it to the UART stream.
 
# Snapshot storage
temps = [ERROR, ERROR, ERROR, ERROR]
rhs = [ERROR, ERROR, ERROR, ERROR]
sensor_health = [0, 0, 0, 0]

def safe_read(sensor):
    try:
        t = sensor.temperature
        h = sensor.relative_humidity
        if (t < TEMP_MIN) or (t > TEMP_MAX) or (h < RH_MIN) or (h > RH_MAX):
            return ERROR, ERROR, 0
        return t, h, 1
    except Exception:
        return ERROR, ERROR, 0
        
def clear_and_title(title):
    black_screen()
    title_label = label.Label(
        terminalio.FONT,
        text=title,
        color=0xFFFFFF,
        x=2,
        y=10,
    )
    splash.append(title_label)


def scpi_sample(n):
    for _ in range(n):
        t0, h0, _ = safe_read(sensor0)
        t1, h1, _ = safe_read(sensor1)
        t2, h2, _ = safe_read(sensor2)
        t3, h3, _ = safe_read(sensor3)

        row = f"{t0:.3f},{h0:.3f},{t1:.3f},{h1:.3f},{t2:.3f},{h2:.3f},{t3:.3f},{h3:.3f}"
        print(row)
        time.sleep(0.1)  # sampling interval (adjust as needed)
    

import sys
import supervisor

def read_command():
    """Return a full line from USB/serial if available, else None."""
    if supervisor.runtime.serial_bytes_available:
        line = sys.stdin.readline().strip()
        return line.upper()
    return None
    
while True:
    cmd = read_command()
    if cmd:
        if cmd.startswith("SAMPLE"):
            try:
                _, n_str = cmd.split()
                n = int(n_str)
                print(f"# SAMPLING {n} ROWS")
                scpi_sample(n)
                print("# DONE")
            except Exception as e:
                print(f"# ERROR: {e}")

    # your display/UI logic continues here
    acquire_snapshot()
    display.refresh()
    time.sleep(0.05)