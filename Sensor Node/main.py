from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from sx1262 import SX1262
import machine
import time
from ublox_gps import MicropyGPS

from machine import Pin, UART
from utime import sleep_ms,ticks_ms

#THIS UNIQUE SENSOR CONFIG

SENSOR_ID = "03"
SENSOR_TYPE = "_accel"

LED = Pin(25, Pin.OUT)

# sensor config
bus = 0
scl = machine.Pin(1)
sda = machine.Pin(0)
freq= 400_000

# Sensor object
motion = PiicoDev_LIS3DH(bus=bus, scl=scl, sda=sda, freq=freq)

# GPS parser
gps = MicropyGPS()
gps_nmea = None

#GPS update rate
UPDATE_GPS = const(10000)
update_gps = ticks_ms()

gps_good = False

latlong_string = "+000.0000000+000.0000000"
epoch_string = "0000000000"
# GPS uart channel config
uart = UART(1, 9600,tx=Pin(4), rx=Pin(5)) 
uart.init(9600, bits=8, parity=None, stop=1)

# Enter low power mode for GPS

#uart.write("$PUBX,40,GLL,0,0,0,0*5C\r\n")


# Config the SPI bus for LoRa
sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=917.2, bw=125.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)

# LoRa receive message callback (not needed for node, but still)
def receive_callback(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        if msg != None:
            error = SX1262.STATUS[err]
            print(msg.decode("utf-8"))
            
# Configure the receive LoRa callback
sx.setBlockingCallback(False, receive_callback)



def read_nmea():

    raw = uart.read()
    global latlong_string
    global epoch_string
    global gps_good
    
    #Sometimes the raw capture from the gps is none
    if raw != None:
        gps.updateall(raw)

        #convert to decimal degrees
        my_lat = gps.latitude[0] + gps.latitude[1]/60
        my_long = gps.longitude[0] + gps.longitude[1]/60

        lat_pre = '+'
        long_pre = '+'
        
        if gps.latitude[2] == 'S':
            lat_pre = '-'
        if gps.latitude[2] == 'W':
            long_pre = '-'
        if my_lat == 0.0 or my_long == 0.0:
            print("Waiting for GPS lock")
        else:
            latlong_string = f"{lat_pre}{my_lat:011.7f}{long_pre}{my_long:011.7f}"
            epoch_string = f"{time.mktime((gps.date[2]+2000,gps.date[1],gps.date[0],gps.timestamp[0],gps.timestamp[1],int(gps.timestamp[2]),0,0))}"
            print(f"{latlong_string}{epoch_string}")
  #GPS issues
        #print("gps issue")
    gps.stringclean()
    sleep_ms(1000)
        
    return True

def build_payload(latlong_string, epoch_string, message_type=9, confidence="00"):
    
    payload_string = f"{message_type}{SENSOR_ID}{SENSOR_TYPE}{latlong_string}{epoch_string}{confidence}"
    
    payload_bytes = payload_string.encode('utf-8')
        
    return payload_bytes



while True:
    
    motion_shake = 0
    
    try:
        motion_shake = motion.shake()
        
    except:  #motion sensor issues
        sleep_ms(500)
        print("sensorissue")
        
    if motion_shake > 10:
        
        #important, stay awake!
        LED.value(1)
        old_shake = motion_shake
        
        # To counter any mis reads or minor shakes, let's wait for .5 sec and read again
        sleep_ms(500)
        
        try:
            motion_shake = motion.shake()
        except:  #motion sensor issues
            sleep_ms(500)
            print("sensorissue")
            
        if old_shake == motion_shake:
            try:
                # likely the sensor has reset and needs to be re-established
                motion = PiicoDev_LIS3DH(bus=bus, scl=scl, sda=sda, freq=freq)
                motion_shake = motion.shake()
            except:  #motion sensor issues
                sleep_ms(500)
                print("sensorissue")

        if motion_shake > 10 and old_shake != motion_shake:
            #important, stay awake!
            
            print("ALARM")
            # We definitely have a thing to be curious about, send an alert
            update_gps = ticks_ms()
            read_nmea()
            sx.send(build_payload(latlong_string, epoch_string, 1, f"{int(motion_shake):02d}"))
            print("sent event")
            
            # there is a chance we could send a heartbeat, so let's give it time to prioritise the event msg
            sleep_ms(2000)


        LED.value(0)
        
    if ticks_ms() - update_gps >= UPDATE_GPS:
        #important, stay awake!
        #sx.send("901accel_-035.4260349+149.2366052168276874300".encode('utf-8'))
        #print("sent test hb")
        update_gps = ticks_ms()
        read_nmea()
        
        #send heartbeat

        sx.send(build_payload(latlong_string, epoch_string, 9, "00"))
        #Save these values
        old_latlong_string = latlong_string
        old_epoch_string = epoch_string
        
        LED.value(1)
        sleep_ms(500)
        LED.value(0)
        print("sent heartbeat")
        
        sleep_ms(500)

