from sx1262 import SX1262
from machine import Pin, UART

import time
from utime import sleep_ms,ticks_ms

LED = Pin(25, Pin.OUT)

#Config the UART bus
uart = UART(0, baudrate=9600, tx= Pin(0), rx=Pin(1),bits=8, parity=None, stop=1)
#uart.init(9600, bits=8, parity=None, stop=1)

# Config the SPI bus for LoRa
sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
sx.begin(freq=917.2, bw=125.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)


# LoRa receive message callback
def receive_callback(events):
    if events & SX1262.RX_DONE:
        msg, err = sx.recv()
        if msg != None:
            LED.value(1)
            sleep_ms(1000)
            LED.value(0)
            error = SX1262.STATUS[err]
            print(msg.decode("utf-8"))
            send_UART(msg.decode("utf-8"))
        
      
# Send UART to Argon function
def send_UART(msg):
    
    uart.write(f"{msg}\n")
    

# Configure the receive LoRa callback
sx.setBlockingCallback(False, receive_callback)

now = ticks_ms()

while True:
    
    if ticks_ms() - now >= 2000:
       now = ticks_ms()
       
       #send_UART("901accel_-035.4260349+149.2366052168276874300")
        


