'''
PiicoDev.py: Unifies I2C drivers for different builds of MicroPython
Changelog:
    - 2022-10-13 P.Johnston Add helptext to run i2csetup script on Raspberry Pi
    - 2022-10-14 M.Ruppe Explicitly set default I2C initialisation parameters for machine-class (Raspberry Pi Pico + W)
    - 2023-01-31 L.Howell Add minimal support for ESP32
    - 2023-05-12 B.Fairleigh to delete a large chunk of unneeded components (only works with pi pico)
'''
import os

_SYSNAME = os.uname().sysname
compat_ind = 1
i2c_err_str = 'PiicoDev could not communicate with module at address 0x{:02X}, check wiring'
setupi2c_str = ', run "sudo curl -L https://piico.dev/i2csetup | bash". Suppress this warning by setting suppress_warnings=True'


from machine import I2C, Pin
from utime import sleep_ms




class I2CUnifiedMachine():
    def __init__(self, bus=None, freq=None, sda=None, scl=None):
        if bus is not None and freq is not None and sda is not None and scl is not None:
            print('Using supplied freq, sda and scl to create machine I2C')
            self.i2c = I2C(bus, freq=freq, sda=sda, scl=scl)
        elif _SYSNAME == 'esp32' and (bus is None and freq is None and sda is None and scl is None):
            raise Exception('Please input bus, frequency, machine.pin SDA and SCL objects to use ESP32')
        else:
            self.i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)

        self.writeto_mem = self.i2c.writeto_mem
        self.readfrom_mem = self.i2c.readfrom_mem



def create_unified_i2c(bus=None, freq=None, sda=None, scl=None, suppress_warnings=True):

    i2c = I2CUnifiedMachine(bus=bus, freq=freq, sda=sda, scl=scl)
    return i2c