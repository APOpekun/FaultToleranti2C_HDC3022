import time
import board
import digitalio
import displayio
import adafruit_hdc302x
import terminalio
from adafruit_display_text import label

# Release any resources currently in use for the displays
displayio.release_displays()

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT, rotation=0)

# Make the display context
splash = displayio.Group()
display.root_group = splash

# Use for I2C
i2c = board.I2C()  # uses board.SCL and board.SDA
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

#define the 4 sensors
sensor0 = adafruit_hdc302x.HDC302x(i2c, device_address=0x44)
sensor1 = adafruit_hdc302x.HDC302x(i2c, device_address=0x45)
sensor2 = adafruit_hdc302x.HDC302x(i2c, device_address=0x46)
sensor3 = adafruit_hdc302x.HDC302x(i2c, device_address=0x47)

# Define button inputs
button_a = digitalio.DigitalInOut(board.D9)
button_b = digitalio.DigitalInOut(board.D6)
button_c = digitalio.DigitalInOut(board.D5)
button_a.switch_to_input(pull=digitalio.Pull.UP)
button_b.switch_to_input(pull=digitalio.Pull.UP)
button_c.switch_to_input(pull=digitalio.Pull.UP)

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

#Buttons
# For main menu use this menu
#Button A Manual 
#Button B <blank>
#Button C Auto

# For 1-10 use this menu
#Button A Prev 
#Button B ESC
#Button C Next

# For 11 use this menu
#Button A Stop 
#Button B ESC
#Button C Run

# Define states
STATE_MAIN_MENU = 0 # Start Here


STATE_AQUIRE = 1 #Quad Display Sensor Health
#Try to query each sensor with the commands below if the sensor does not respond return the float 
#use a single function like safe_read(sensor) that returns (temp, rh) with fallback values
##Accepted range
TEMP_MIN = -40.0
TEMP_MAX = 125.0
RH_MIN = 0.0
RH_MAX = 100.0
#Sensor Health array 1=good, 0=bad
sensor_health = [1, 1, 1, 1]

# Fall back
ERROR = -100.00

#- Question: How do you want “health” defined
#- Answer: show each sensor’s T/RH with a label like OK vs ERR (based on safe_read success).

#0x44
#sensor0.temperature
#sensor0.relative_humidity
#0x45
#sensor1.temperature
#sensor1.relative_humidity
#0x46
#sensor2.temperature
#sensor2.relative_humidity
#0x47
#sensor3.temperature
#sensor3.relative_humidity


STATE_TEMP_QUAD_RAW = 2 #Quad Display Temp
#divide the 128x64 screen into quadrants and print the raw data
# Draw vertical lines middle and horizontal but no need for a border box. Text only. in the center Place a T for Temp
#Set float precision at 2 places
# 0x44 | 0x45
# -----T-----
# 0x46 | 0x47

STATE_RH_QUAD_RAW = 3 #Quad Display RH
#divide the 128x64 screen into quadrants and print the raw data
# Draw vertical lines middle and horizontal but no need for a border box. Text only. in the center Place a H for RH
# 0x44 | 0x45
# -----H-----
# 0x46 | 0x47

STATE_MEAN_DUAL = 4
#divide the 128x64 screen into half and print the average of each meaurement
# Temp | RH

STATE_TEMP_DEVIATION = 5
# For each sample compute dT_n = abs(X_n - u)
# where x_n is the temperature for each channel
# and u is the mean calculated in step 4
#divide the 128x64 screen into quadrants and print the deviation data
# 0x44 | 0x45
# -----------
# 0x46 | 0x47

STATE_RH_DEVIATION = 6
# For each sample compute dH_n = abs(Y_n - u)
# where Y_n is the temperature for each channel
# and u is the mean calculated in step 4
#divide the 128x64 screen into quadrants and print the deviation data
# 0x44 | 0x45
# -----------
# 0x46 | 0x47

STATE_MEDIAN_AVERAGE_DEVIATION = 7
#divide the 128x64 screen into half and print the median of each deviaton (MAD)
# Temp | RH
#Default to PopMAD but have an argument toggle to Scaled MAD


#afor NORMDEV use A configurable threshold constant preset to 3

STATE_TEMP_NORMDEV = 8
# For each sample compute zT_n = dT_n / MADT
# where dT_n is the deviation from the median for each channel
#divide the 128x64 screen into quadrants and print the deviation data
# 0x44 | 0x45
# -----------
# 0x46 | 0x47

#IF the deviation is more than 3 put a * infront of the number where the minus sign might go eg *3.4

STATE_RH_NORMDEV = 9
# For each sample compute zH_n = dH_n / MADH
# where dH_n is the deviation from the median for each channel
#divide the 128x64 screen into quadrants and print the deviation data
# 0x44 | 0x45
# -----------
# 0x46 | 0x47

#IF the deviation is more than 3 put a * infront of the number where the minus sign might go eg *3.4


STATE_OUTPUT = 10
#divide the 128x64 screen into half and print the average of the accepted meaurements
# Temp | RH
#- Only sensors with z < 3 included
#if only 2 sensors are used put an Astrics

STATE_RUN = 11
Take the function blocks use in all the previous states and chain them. the screen matches 10. this is the live dash board update 1Hz with reconfigurable delay




#follow the transition table 
#Btn A is Prev Where logically allowed
#Btn B is Escape to main menu
#Btn C is Next Where logically allowed

# Transition TABLE
# in | btnA | btnB | btnC
#  0 |   1  |   0  |  10
#  1 |   1  |   0  |   2
#  2 |   1  |   0  |   3
#  3 |   2  |   0  |   4
#  4 |   3  |   0  |   5
#  5 |   4  |   0  |   6
#  6 |   5  |   0  |   7
#  7 |   6  |   0  |   8
#  8 |   7  |   0  |   9
#  9 |   8  |   0  |  10
# 10 |   9  |   0  |   1
# 11 |  11  |   0  |  11



#5. Button behavior details
#- Question: Do you want edge-triggered behavior (on button press transition once) with simple debouncing?
#- I’d implement: “act only when button goes from high→low, then ignore for ~150 ms”.
#- answer: attach the buttons to an interupt: on rising edge latch the future state change then when the rest of the step finishes

#- Question: from any state, should B always go straight to STATE_MAIN_MENU, even from STATE_RUN?
#- Answer: yes


#6. Sampling model
#For all the analysis states (2–10):
#- Question: Should each state:
#- Answer: Use a single snapshot taken in STATE_AQUIRE and reuse those values through the whole sequence?
#acquire once, then walk through the analysis of that same sample.

#- Question: How should the delay be reconfigured?
#- Answer: Hard-coded constant at top of file (e.g., RUN_DELAY = 1.0)


#8. Error / missing sensor indication
#When safe_read fails and returns -100.0:
#- Question: How should that be shown on screen?
#DNR  - Did Not Respond


#- Main menu text content (STATE_MAIN_MENU):
#What exact text do you want on screen? For example:
#- Center screen: HDC302x Quad Analyzer
#- Left edge
#- Line 1: A: Manual
#- Line 3: C: Auto
#I can Tune and massage the formating as needed


# Initialize state
current_state = STATE_MAIN_MENU



# the above was given to MSFT copilot. there were several rounds of back and forth where I asked copilot to ask clarifying questions and I answered the questions in the code then shared the whole code again.

#ALL following code is AI generated
#ADD BELOW HERE
# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
RUN_DELAY = 1.0          # seconds between updates in STATE_RUN
NORMDEV_THRESHOLD = 3.0  # z-score threshold for acceptance

# Snapshot storage
temps = [ERROR, ERROR, ERROR, ERROR]
rhs = [ERROR, ERROR, ERROR, ERROR]
sensor_health = [0, 0, 0, 0]

mean_T = 0.0
mean_H = 0.0
dT = [0.0, 0.0, 0.0, 0.0]
dH = [0.0, 0.0, 0.0, 0.0]
MAD_T = 0.0
MAD_H = 0.0
zT = [0.0, 0.0, 0.0, 0.0]
zH = [0.0, 0.0, 0.0, 0.0]

snapshot_valid = False
run_enabled = False
last_run_update = 0.0

# Button edge tracking (pull-ups: True = idle, False = pressed)
last_a = button_a.value
last_b = button_b.value
last_c = button_c.value


# ---------------------------------------------------------------------------
# Helpers: math
# ---------------------------------------------------------------------------
def safe_read(sensor):
    try:
        t = sensor.temperature
        h = sensor.relative_humidity
        if (t < TEMP_MIN) or (t > TEMP_MAX) or (h < RH_MIN) or (h > RH_MAX):
            return ERROR, ERROR, 0
        return t, h, 1
    except Exception:
        return ERROR, ERROR, 0


def mean_of(values, health_mask):
    total = 0.0
    count = 0
    for v, ok in zip(values, health_mask):
        if ok and v != ERROR:
            total += v
            count += 1
    if count == 0:
        return 0.0
    return total / count


def median_of(values, health_mask):
    valid = [v for v, ok in zip(values, health_mask) if ok and v != ERROR]
    if not valid:
        return 0.0
    valid.sort()
    n = len(valid)
    mid = n // 2
    if n % 2 == 1:
        return valid[mid]
    return 0.5 * (valid[mid - 1] + valid[mid])


def mad_of(values, health_mask, use_scaled=False):
    med = median_of(values, health_mask)
    devs = []
    for v, ok in zip(values, health_mask):
        if ok and v != ERROR:
            devs.append(abs(v - med))
    if not devs:
        return 0.0
    devs.sort()
    n = len(devs)
    mid = n // 2
    if n % 2 == 1:
        mad = devs[mid]
    else:
        mad = 0.5 * (devs[mid - 1] + devs[mid])
    if use_scaled:
        mad *= 1.4826
    return mad


def compute_z_scores(devs, mad):
    if mad == 0.0:
        return [0.0 for _ in devs]
    return [d / mad for d in devs]


# ---------------------------------------------------------------------------
# Helpers: drawing
# ---------------------------------------------------------------------------
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


def draw_main_menu():
    black_screen()
    title = label.Label(
        terminalio.FONT,
        text="HDC302x Quad Analyzer",
        color=0xFFFFFF,
        x=2,
        y=12,
    )
    a_label = label.Label(
        terminalio.FONT,
        text="A: Manual",
        color=0xFFFFFF,
        x=2,
        y=32,
    )
    c_label = label.Label(
        terminalio.FONT,
        text="C: Auto",
        color=0xFFFFFF,
        x=2,
        y=48,
    )
    splash.append(title)
    splash.append(a_label)
    splash.append(c_label)


def draw_quad(title_char, values, labels, units=None):
    # values: list of 4 strings already formatted
    black_screen()
    center_label = label.Label(
        terminalio.FONT,
        text=title_char,
        color=0xFFFFFF,
        x=WIDTH // 2 - 3,
        y=HEIGHT // 2 + 4,
    )
    splash.append(center_label)

    # Quadrant positions (approximate centers)
    positions = [
        (8, 16),   # top-left
        (72, 16),  # top-right
        (8, 48),   # bottom-left
        (72, 48),  # bottom-right
    ]

    for i in range(4):
        x, y = positions[i]
        text = "{} {}".format(labels[i], values[i])
        lbl = label.Label(
            terminalio.FONT,
            text=text,
            color=0xFFFFFF,
            x=x,
            y=y,
        )
        splash.append(lbl)


def draw_dual(title, left_label, left_value, right_label, right_value):
    black_screen()
    title_label = label.Label(
        terminalio.FONT,
        text=title,
        color=0xFFFFFF,
        x=2,
        y=10,
    )
    left = label.Label(
        terminalio.FONT,
        text="{} {}".format(left_label, left_value),
        color=0xFFFFFF,
        x=2,
        y=36,
    )
    right = label.Label(
        terminalio.FONT,
        text="{} {}".format(right_label, right_value),
        color=0xFFFFFF,
        x=WIDTH // 2 + 2,
        y=36,
    )
    splash.append(title_label)
    splash.append(left)
    splash.append(right)


def format_value(v, with_units=None, decimals=2):
    if v == ERROR:
        return "DNR"
    fmt = "{:0." + str(decimals) + "f}"
    s = fmt.format(v)
    if with_units == "C":
        return s + "C"
    if with_units == "%":
        return s + "%"
    return s


def format_z(z):
    mark = "*" if abs(z) > NORMDEV_THRESHOLD else ""
    fmt = "{:0.2f}"
    return mark + fmt.format(z)


# ---------------------------------------------------------------------------
# Snapshot + analysis
# ---------------------------------------------------------------------------
def acquire_snapshot():
    global temps, rhs, sensor_health
    global mean_T, mean_H, dT, dH, MAD_T, MAD_H, zT, zH
    global snapshot_valid

    t0, h0, ok0 = safe_read(sensor0)
    t1, h1, ok1 = safe_read(sensor1)
    t2, h2, ok2 = safe_read(sensor2)
    t3, h3, ok3 = safe_read(sensor3)

    temps = [t0, t1, t2, t3]
    rhs = [h0, h1, h2, h3]
    sensor_health = [ok0, ok1, ok2, ok3]

    mean_T = mean_of(temps, sensor_health)
    mean_H = mean_of(rhs, sensor_health)

    for i in range(4):
        if sensor_health[i] and temps[i] != ERROR:
            dT[i] = abs(temps[i] - mean_T)
        else:
            dT[i] = 0.0
        if sensor_health[i] and rhs[i] != ERROR:
            dH[i] = abs(rhs[i] - mean_H)
        else:
            dH[i] = 0.0

    MAD_T = mad_of(temps, sensor_health, use_scaled=False)
    MAD_H = mad_of(rhs, sensor_health, use_scaled=False)

    zT_vals = compute_z_scores(dT, MAD_T)
    zH_vals = compute_z_scores(dH, MAD_H)
    for i in range(4):
        zT[i] = zT_vals[i]
        zH[i] = zH_vals[i]

    snapshot_valid = True


# ---------------------------------------------------------------------------
# State renderers
# ---------------------------------------------------------------------------
def render_state_main_menu():
    draw_main_menu()


def render_state_acquire():
    acquire_snapshot()
    labels = ["44", "45", "46", "47"]
    vals = []
    for i in range(4):
        if not sensor_health[i] or temps[i] == ERROR or rhs[i] == ERROR:
            vals.append("DNR ERR")
        else:
            t_str = format_value(temps[i], "C")
            h_str = format_value(rhs[i], "%")
            vals.append("{} {}".format(t_str, h_str))
    draw_quad("S", vals, labels)


def render_state_temp_quad_raw():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = [format_value(t, "C") for t in temps]
    draw_quad("T", vals, labels)


def render_state_rh_quad_raw():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = [format_value(h, "%") for h in rhs]
    draw_quad("H", vals, labels)


def render_state_mean_dual():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    t_str = format_value(mean_T, "C")
    h_str = format_value(mean_H, "%")
    draw_dual("Mean", "T", t_str, "RH", h_str)


def render_state_temp_deviation():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = ["{:0.2f}".format(v) for v in dT]
    draw_quad("dT", vals, labels)


def render_state_rh_deviation():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = ["{:0.2f}".format(v) for v in dH]
    draw_quad("dH", vals, labels)


def render_state_mad():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    t_str = "{:0.2f}".format(MAD_T)
    h_str = "{:0.2f}".format(MAD_H)
    draw_dual("MAD (Pop)", "T", t_str, "RH", h_str)


def render_state_temp_normdev():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = [format_z(z) for z in zT]
    draw_quad("zT", vals, labels)


def render_state_rh_normdev():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return
    labels = ["44", "45", "46", "47"]
    vals = [format_z(z) for z in zH]
    draw_quad("zH", vals, labels)


def render_state_output():
    if not snapshot_valid:
        clear_and_title("No Data - Run Acquire")
        return

    accepted_T = []
    accepted_H = []
    for i in range(4):
        if sensor_health[i] and temps[i] != ERROR and rhs[i] != ERROR:
            if abs(zT[i]) < NORMDEV_THRESHOLD and abs(zH[i]) < NORMDEV_THRESHOLD:
                accepted_T.append(temps[i])
                accepted_H.append(rhs[i])

    if not accepted_T:
        clear_and_title("No Accepted Sensors")
        return

    mean_t = sum(accepted_T) / len(accepted_T)
    mean_h = sum(accepted_H) / len(accepted_H)

    t_str = format_value(mean_t, "C")
    h_str = format_value(mean_h, "%")

    if len(accepted_T) == 2:
        t_str = "*" + t_str
        h_str = "*" + h_str

    draw_dual("Output", "T", t_str, "RH", h_str)


def render_state_run():
    # Layout matches OUTPUT, but live and periodic
    global last_run_update
    now = time.monotonic()
    if not run_enabled:
        clear_and_title("Run: Stopped")
        return
    if now - last_run_update < RUN_DELAY:
        return
    last_run_update = now

    acquire_snapshot()

    accepted_T = []
    accepted_H = []
    for i in range(4):
        if sensor_health[i] and temps[i] != ERROR and rhs[i] != ERROR:
            if abs(zT[i]) < NORMDEV_THRESHOLD and abs(zH[i]) < NORMDEV_THRESHOLD:
                accepted_T.append(temps[i])
                accepted_H.append(rhs[i])

    if not accepted_T:
        clear_and_title("Run: No Accepted")
        return

    mean_t = sum(accepted_T) / len(accepted_T)
    mean_h = sum(accepted_H) / len(accepted_H)

    t_str = format_value(mean_t, "C")
    h_str = format_value(mean_h, "%")

    if len(accepted_T) == 2:
        t_str = "*" + t_str
        h_str = "*" + h_str

    draw_dual("Run", "T", t_str, "RH", h_str)


# ---------------------------------------------------------------------------
# State dispatch
# ---------------------------------------------------------------------------
def render_current_state():
    if current_state == STATE_MAIN_MENU:
        render_state_main_menu()
    elif current_state == STATE_AQUIRE:
        render_state_acquire()
    elif current_state == STATE_TEMP_QUAD_RAW:
        render_state_temp_quad_raw()
    elif current_state == STATE_RH_QUAD_RAW:
        render_state_rh_quad_raw()
    elif current_state == STATE_MEAN_DUAL:
        render_state_mean_dual()
    elif current_state == STATE_TEMP_DEVIATION:
        render_state_temp_deviation()
    elif current_state == STATE_RH_DEVIATION:
        render_state_rh_deviation()
    elif current_state == STATE_MEDIAN_AVERAGE_DEVIATION:
        render_state_mad()
    elif current_state == STATE_TEMP_NORMDEV:
        render_state_temp_normdev()
    elif current_state == STATE_RH_NORMDEV:
        render_state_rh_normdev()
    elif current_state == STATE_OUTPUT:
        render_state_output()
    elif current_state == STATE_RUN:
        render_state_run()


# Transition table (excluding ESC and RUN special behavior)
transition_table = {
    (STATE_MAIN_MENU, "A"): STATE_AQUIRE,
    (STATE_MAIN_MENU, "C"): STATE_OUTPUT,  # per table; AUTO path
    (STATE_AQUIRE, "A"): STATE_AQUIRE,
    (STATE_AQUIRE, "C"): STATE_TEMP_QUAD_RAW,
    (STATE_TEMP_QUAD_RAW, "A"): STATE_AQUIRE,
    (STATE_TEMP_QUAD_RAW, "C"): STATE_RH_QUAD_RAW,
    (STATE_RH_QUAD_RAW, "A"): STATE_TEMP_QUAD_RAW,
    (STATE_RH_QUAD_RAW, "C"): STATE_MEAN_DUAL,
    (STATE_MEAN_DUAL, "A"): STATE_RH_QUAD_RAW,
    (STATE_MEAN_DUAL, "C"): STATE_TEMP_DEVIATION,
    (STATE_TEMP_DEVIATION, "A"): STATE_MEAN_DUAL,
    (STATE_TEMP_DEVIATION, "C"): STATE_RH_DEVIATION,
    (STATE_RH_DEVIATION, "A"): STATE_TEMP_DEVIATION,
    (STATE_RH_DEVIATION, "C"): STATE_MEDIAN_AVERAGE_DEVIATION,
    (STATE_MEDIAN_AVERAGE_DEVIATION, "A"): STATE_RH_DEVIATION,
    (STATE_MEDIAN_AVERAGE_DEVIATION, "C"): STATE_TEMP_NORMDEV,
    (STATE_TEMP_NORMDEV, "A"): STATE_MEDIAN_AVERAGE_DEVIATION,
    (STATE_TEMP_NORMDEV, "C"): STATE_RH_NORMDEV,
    (STATE_RH_NORMDEV, "A"): STATE_TEMP_NORMDEV,
    (STATE_RH_NORMDEV, "C"): STATE_OUTPUT,
    (STATE_OUTPUT, "A"): STATE_RH_NORMDEV,
    (STATE_OUTPUT, "C"): STATE_AQUIRE,
}


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
render_current_state()

while True:
    global last_a, last_b, last_c, current_state, run_enabled

    # Read current button values
    va = button_a.value
    vb = button_b.value
    vc = button_c.value

    # Rising edges (False -> True, since pull-up)
    a_rise = (last_a is False) and (va is True)
    b_rise = (last_b is False) and (vb is True)
    c_rise = (last_c is False) and (vc is True)

    last_a = va
    last_b = vb
    last_c = vc

    # ESC from any state
    if b_rise:
        current_state = STATE_MAIN_MENU
        run_enabled = False
        render_current_state()
        continue

    # Special behavior for STATE_RUN
    if current_state == STATE_RUN:
        if a_rise:
            # Stop
            run_enabled = False
            render_current_state()
        if c_rise:
            # Run
            run_enabled = True
            render_current_state()
        # Periodic update handled inside render_state_run
        render_state_run()
        time.sleep(0.01)
        continue

    # From main menu: allow direct jump to RUN on Auto if you want live mode
    if current_state == STATE_MAIN_MENU and c_rise:
        # If you prefer table behavior only, comment the next two lines
        current_state = STATE_RUN
        run_enabled = True
        render_current_state()
        time.sleep(0.01)
        continue

    # Normal transitions via table
    key = None
    if a_rise:
        key = (current_state, "A")
    elif c_rise:
        key = (current_state, "C")

    if key in transition_table:
        current_state = transition_table[key]
        # entering RUN via table is not defined; RUN handled above
        render_current_state()

    time.sleep(0.01)