"""
.. module:: htu21d

*************
HTU21D Module
*************

This module contains the driver for MEAS HTU21D Relative Humidity and Temperature sensor.
The HTU21D is capable of direct I2C communication and can be set on 4 different level of resolution in both temperature and humidity measurements (`datasheet <http://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7FHPC199_6%7FA%7Fpdf%7FEnglish%7FENG_DS_HPC199_6_A.pdf%7FCAT-HSC0004>`_).
    """

import i2c

HTU_I2C_ADDRESS = 0x40

HTU21D_TRIGGER_TEMP_HOLD = 0xE3
HTU21D_TRIGGER_HUMD_HOLD = 0xE5
HTU21D_TRIGGER_TEMP_NOHOLD = 0xF3
HTU21D_TRIGGER_HUMD_NOHOLD = 0xF5
HTU21D_WRITE_USER_REG = 0xE6
HTU21D_READ_USER_REG = 0xE7
HTU21D_SOFT_RESET = 0xFE

HTU21D_END_OF_BATTERY_SHIFT = 6
HTU21D_ENABLE_HEATER_SHIFT = 2
HTU21D_DISABLE_OTP_RELOAD = 1
HTU21D_RESERVED_MASK = 0x31

HTU21D_STARTUP_DELAY = 15000
HTU21D_TEMP_MAX_DELAY = 50000

HTU_TEMP_CALIB_OFFSET_0 = 0
HTU_TEMP_CALIB_OFFSET_1 = 4
HTU_TEMP_CALIB_OFFSET_2 = 6

BITRES_HTU_RH_12_TEMP14 = 0x02
BITRES_HTU_RH_8_TEMP12 = 0x03
BITRES_HTU_RH_10_TEMP13 = 0x82
BITRES_HTU_RH_11_TEMP11 = 0x83

BITRES_HTU_LIST = [BITRES_HTU_RH_12_TEMP14, BITRES_HTU_RH_8_TEMP12, BITRES_HTU_RH_10_TEMP13, BITRES_HTU_RH_11_TEMP11]

HTU_DEALY_FOR_TEMP = [50, 13, 25, 7]
HTU_DEALY_FOR_HUMID = [16, 3, 5, 8]


class HTU21D(i2c.I2C):
    """
.. class:: HTU21D(i2cdrv, addr=0x40, clk=400000)

    Creates an intance of a new HTU21D.

    :param i2cdrv: I2C Bus used '( I2C0, ... )'
    :param addr: Slave address, default 0x40
    :param clk: Clock speed, default 400kHz

    Example: ::

        from meas.htu21d import htu21d

        ...

        htu = htu21d.HTU21D(I2C0)
        htu.start()
        htu.init()
        t,h = htu.get_temp_humid()

    """
    # Init

    def __init__(self, i2cdrv, addr=HTU_I2C_ADDRESS, clk=400000):
        i2c.I2C.__init__(self, i2cdrv, addr, clk)
        self._addr = addr

    def init(self, res=0):
        """

.. method:: init(res=0)

        Initialize the HTU21D setting the resolution of the sensor.

        :param res: set the resolution (from 0 to 3) for temperature and humidity measurements according to the table below; default 0.

========= ================ =============== ================ ===============
res value Humid Resolution Temp Resolution Meas. Time Humid Meas. Time Temp
========= ================ =============== ================ ===============
0         12 bits          14 bits         16 ms            50 ms
1         8 bits           12 bits         3 ms             13 ms
2         10 bits          13 bits         5 ms             25 ms
3         11 bits          11 bits         8 ms             7 ms
========= ================ =============== ================ ===============

        """
        self._reset()
        self._set_resolution(0)

    def _reset(self):
        self.write(HTU21D_SOFT_RESET)

    def _set_resolution(self, res):
        if res not in (0, 1, 2, 3):
            res = 0
        self.write_bytes(HTU21D_WRITE_USER_REG, BITRES_HTU_LIST[res])
        self.delay_t = HTU_DEALY_FOR_TEMP[res]
        self.delay_h = HTU_DEALY_FOR_HUMID[res]
        cc = self.write_read(HTU21D_READ_USER_REG,1)[0]

    def _wait(self, measure):
        if measure == "temp":
            sleep(self.delay_t)
        elif measure == "humid":
            sleep(self.delay_h)

    def get_raw_temp(self):
        """

.. method:: get_raw_temp()

        Retrieves the current temperature data from the sensor as raw value.

        Returns raw_temp

        """
        self.write(HTU21D_TRIGGER_TEMP_NOHOLD)
        self._wait("temp")
        data = self.read(2)
        raw_temp = (data[0] << 8) | (data[1] & 0xFC)
        return raw_temp
    
    def get_raw_humid(self):
        """

.. method:: get_raw_humid()

        Retrieves the current humidity data from the sensor as raw value.

        Returns raw_humid

        """
        self.write(HTU21D_TRIGGER_HUMD_NOHOLD)
        self._wait("humid")
        data = self.read(2)
        raw_humid = (data[0] << 8) | (data[1] & 0xFC)
        return raw_humid
        
    def get_temp(self):
        """

.. method:: get_temp()

        Retrieves the current temperature data from the sensor as calibrate value in °C.

        Returns temp

        """
        raw = self.get_raw_temp(self)
        temp = ((175.72*raw)/(65536))-46.85
        return temp
    
    def get_humid(self):
        """

.. method:: get_humid()

        Retrieves the current relative humidity data from the sensor as calibrate value in %RH.

        Returns humid

        """
        raw = self.get_raw_humid(self)
        humid = ((125*raw)/(65536))-6
        return humid
    
    def get_temp_humid(self):
        """

.. method:: get_temp_humid()

        Retrieves both temperature and humidity in one call.

        Returns temp, humid

        """
        temp = self.get_temp()
        humid = self.get_humid()
        return temp, humid
