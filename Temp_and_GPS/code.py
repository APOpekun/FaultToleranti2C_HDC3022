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

from adafruit_pcf8523.pcf8523 import PCF8523 #reserved for RTC
#Reserved for SD card ReadWrite
# Initialize display
displayio.release_displays()

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

rtc = PCF8523(i2c)

#initialize GPS
# Connect UART rx to GPS module TX, and UART tx to GPS module RX.
tx = board.TX  # Use board.GP4 or other UART TX on Raspberry Pi Pico boards.
rx = board.RX  # Use board.GP5 or other UART RX on Raspberry Pi Pico boards.
uart = busio.UART(tx, rx, baudrate=9600, timeout=10)
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

# Turn on the basic GGA and RMC info (what you typically want)
#gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on everything (not all of it is parsed!)
gps.send_command(b'$PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n')

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
    rotation=270
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

STATE_IDLE = 0
STATE_GPS_WAIT = 1
STATE_LOGGING = 2

state = STATE_IDLE
gps_lock_counter = 0
GPS_LOCK_REQUIRED = 25   # seconds of stable fix

last_log_time = 0.0          # for 1 Hz logging
LOG_PERIOD    = 1.0          # seconds

last_rtc_sync = 0.0          # for GPS→RTC discipline
RTC_SYNC_PERIOD = 60.0      # seconds (10 minutes)

def button_pressed(btn, last):
    pressed = (last and not btn.value)
    return pressed


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
def sync_rtc_from_gps(gps, rtc):
    # Must have fix AND valid timestamp
    if not gps.has_fix or gps.timestamp_utc is None:
        print("RTC sync skipped: no GPS fix")
        return
    ts = gps.timestamp_utc
    
    # GPS sometimes reports year=0 briefly even after fix
    if ts.tm_year < 2000 or ts.tm_year > 2099:
        print("RTC sync skipped: GPS year invalid:", ts.tm_year)
        return
    # PCF8523 stores year as 0–99 (representing 2000–2099) the conversion is handled internally
    t = time.struct_time((
        ts.tm_year,          # YEAR (0–99)
        ts.tm_mon,         # MONTH
        ts.tm_mday,        # DAY
        ts.tm_hour,        # HOUR
        ts.tm_min,         # MINUTE
        ts.tm_sec,         # SECOND
        ts.tm_wday,        # WEEKDAY (0–6)
        ts.tm_yday,        # YEARDAY (ignored)
        -1                 # isdst (ignored)
    ))
    rtc.datetime = t
    print("RTC synced from GPS:", t)
    
def TS_from_gps_rtc(gps, rtc):
    # Must have fix AND valid timestamp
    if not gps.has_fix or gps.timestamp_utc is None:
        ts = rtc.datetime
        
    else:
        ts = gps.timestamp_utc
    return ts


def Aquire(Sensors):
    temps = []
    for i, sensor in enumerate(Sensors):
        t, ok = safe_read(sensor)
        sensor_health[i] = ok
        temps.append(t)
    #timestamp = "Day Mon N HH:MM:SS.ssss YYYY" #from GPS or RTC Not available yet
    return temps

def PrintGPS(gps):
    print(gps.nmea_sentence)
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
    print(f"Lat/Long: {gps.latitude:.6f}°,{gps.longitude:.6f}°")
    print(f"{gps.latitude_degrees}°, {gps.latitude_minutes:2.4f}', {gps.longitude_degrees}°, {gps.longitude_minutes:2.4f}'")
    print(f"Fix quality: {gps.fix_quality}")
    print("=" * 40)  # Print a separator line.

def build_csv_row(ts, temps, v, p):
    date_str = f"{ts.tm_year:04d}-{ts.tm_mon:02d}-{ts.tm_mday:02d}"
    time_str = f"{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d}"

    temp_strs = [f"{t:0.4f}" for t in temps]

    v = max17.cell_voltage
    p = max17.cell_percent
    batt_v_str = f"{v:0.4f}"
    batt_p_str = f"{p:0.2f}"

    row = date_str + "," + time_str + "," + ",".join(temp_strs) + "," + batt_v_str + "," + batt_p_str
    return row

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
rtc_lock = False


printed = False

while True:
    gps.update()   # ALWAYS update GPS
    
    now = time.monotonic()
    
    # Button edges
    a_press = button_pressed(button_a, last_a)
    b_press = button_pressed(button_b, last_b)
    last_a = button_a.value
    last_b = button_b.value

    # Periodic GPS→RTC sync (when we have a fix)
    if gps.has_fix and (now - last_rtc_sync) >= RTC_SYNC_PERIOD:
        sync_rtc_from_gps(gps, rtc)
        last_rtc_sync = now
        
    # -------------------------
    # STATE 0 — IDLE
    # -------------------------
    if state == STATE_IDLE:
        # Show idle screen
        if not printed:
            print("IDLE Press A")
            printed = True
        screen = displayio.Group()
        screen.append(label.Label(terminalio.FONT,
                                  text="IDLE\nPress A",
                                  color=0xFFFFFF, x=5, y=10))
        display.root_group = screen

        if a_press:
            print("Starting GPS acquisition")
            state = STATE_GPS_WAIT
            gps_lock_counter = 0
            printed = False

    # -------------------------
    # STATE 1 — GPS WAIT
    # -------------------------
    elif state == STATE_GPS_WAIT:
        screen = displayio.Group()
        screen.append(label.Label(terminalio.FONT,
                                  text="GPS: acquiring...",
                                  color=0xFFFFFF, x=5, y=10))

        if gps.has_fix and gps.timestamp_utc is not None:
            gps_lock_counter += 1
            screen.append(label.Label(terminalio.FONT,
                                      text=f"Fix {gps_lock_counter}/{GPS_LOCK_REQUIRED}",
                                      color=0xFFFFFF, x=5, y=25))
            if gps_lock_counter >= GPS_LOCK_REQUIRED:
                print("GPS locked. Autostart logging.")
                state = STATE_LOGGING
                last_log_time = now  # align logging start
        else:
            gps_lock_counter = 0

        display.root_group = screen

        if b_press:
            print("GPS aborted. Returning to idle.")
            state = STATE_IDLE

    # -------------------------
    # STATE 2 — LOGGING
    # -------------------------
    elif state == STATE_LOGGING:
        # Toggle logging on/off with B
        if b_press:
            print("Logging stopped. Returning to idle.")
            state = STATE_IDLE
            continue
        # 1 Hz logging
        if (now - last_log_time) >= LOG_PERIOD:
            last_log_time = now
            ts = TS_from_gps_rtc(gps, rtc)
            temps = Aquire(TempSens)
            v = max17.cell_voltage
            p = max17.cell_percent

            row = build_csv_row(ts, temps, v, p)
            
            print(row)  # serial monitor; later: write to SD
                
                #WRITE TO SD CARD HERE
                
            screen = displayio.Group()
            screen.append(label.Label(terminalio.FONT,
                            text="LOGGING",
                            color=0xFFFFFF, x=5, y=10))

            # Display temps
            for i, t in enumerate(temps):
                screen.append(label.Label(terminalio.FONT,
                    text=f"T{i}: {t:0.4f}",
                    color=0xFFFFFF, x=5, y=25 + i*12))

            # Battery
            screen.append(label.Label(terminalio.FONT,
                text=f"{v:.2f}V {p:.1f}%",
                color=0xFFFFFF, x=5, y=120))
            display.root_group = screen
