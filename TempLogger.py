#! ./TempLogger/TempLoggerEnv/bin/python3.11
try:
    import smbus
    import time
    import os
    import csv
except ImportError as e:
    print("pkg not found: {e}")

Temp_Reg = 0x05
i2c_bus=1
i2c = smbus.SMBus(i2c_bus)
# Initialize 8 MCP9808 sensors

def read_MCP9808(bus,address):
        data = bus.read_i2c_block_data(address, Temp_Reg, 2)#read two bytes
        """Internal function to convert temperature given by the sensor"""
        # Clear flags from the value
        data[0] &= 0x1F
        if data[0] & 0x10 == 0x10:
            return ((data[0] & 0x0F) * 16 + data[1] / 16.0) - 256
        return data[0] * 16 + data[1] / 16.0
SECONDS = 0
MINUTES = 5
HOURS = 12
DAYS = 0
RUNTIME = SECONDS + 60*(MINUTES + 60*(HOURS + 24*DAYS))+1 #SECONDS
INTERVAL = 1 #SECONDS

with open("TimeTemp.csv","w",newline="") as f:
    then = time.clock_gettime(time.CLOCK_REALTIME)
    start = then
    ts = time.strftime("%Y %b %d %a %H %M %S",time.localtime(start))
    writer = csv.writer(f)
    
    writer.writerow(["now","Temp1","Temp2","Temp3","Temp4","Temp5","Temp6","Temp7","Temp8"])
    while True:
        try:
            row = []
            now = time.clock_gettime(time.CLOCK_REALTIME)
            for i in range(8):
                    row.append(read_MCP9808(i2c, address=0x18 + i))
            if (now - start)>RUNTIME:
                end = time.clock_gettime(time.CLOCK_REALTIME)
                ts = time.strftime("%Y %b %d %a %H %M %S",time.localtime(end))
                writer.writerow(["Timestamp:",ts,"\tnow:",end])
                break
            if (now - then)>INTERVAL:
                row = [now]+row
                #print(row)
                writer.writerow(row)
                then = now
        except Exception as e:
            print(e)

