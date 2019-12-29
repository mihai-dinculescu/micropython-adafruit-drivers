# MIT License

# MicroPython Port Copyright (c) 2019
# Mihai Dinculescu

# CircuitPython Implementation Copyright (c) 2017
# Dean Miller for Adafruit Industries

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
This is a lightweight port from CircuitPython to MicroPython
of Dean Miller's https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/master/adafruit_seesaw/seesaw.py

* Author(s): Mihai Dinculescu

Implementation Notes
--------------------

**Hardware:**
* Adafruit Adafruit STEMMA Soil Sensor - I2C Capacitive Moisture Sensor: https://www.adafruit.com/product/4026

**Software and Dependencies:**
* MicroPython firmware: https://micropython.org
* SeeSaw Base Class: seesaw.py

**Tested on:**
* Hardware: Adafruit HUZZAH32 - ESP32 Feather https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/overview
* Firmware: MicroPython v1.12 https://micropython.org/resources/firmware/esp32-idf3-20191220-v1.12.bin
"""

import time
import ustruct

import seesaw

_STATUS_TEMP = const(0x04)

_TOUCH_CHANNEL_OFFSET = const(0x10)

class StemmaSoilSensor(seesaw.Seesaw):
    """Driver for Adafruit STEMMA Soil Sensor - I2C Capacitive Moisture Sensor
       :param I2C i2c: I2C bus the SeeSaw is connected to.
       :param int addr: I2C address of the SeeSaw device. Default is 0x36."""
    def __init__(self, i2c, addr=0x36):
        super().__init__(i2c, addr)

    def get_temp(self):
        buf = bytearray(4)
        self._read(seesaw.STATUS_BASE, _STATUS_TEMP, buf, .005)
        buf[0] = buf[0] & 0x3F
        ret = ustruct.unpack(">I", buf)[0]
        return 0.00001525878 * ret

    def get_moisture(self):
        buf = bytearray(2)

        self._read(seesaw.TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, .005)
        ret = ustruct.unpack(">H", buf)[0]
        time.sleep(.001)

        # retry if reading was bad
        count = 0
        while ret > 4095:
            self._read(seesaw.TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, .005)
            ret = ustruct.unpack(">H", buf)[0]
            time.sleep(.001)
            count += 1
            if count > 3:
                raise RuntimeError("Could not get a valid moisture reading.")

        return ret
