#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# See https://docs.pycom.io for more information regarding library specifics

from pycoproc import Pycoproc
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2, PRESSURE


def py_connection():
    py = Pycoproc()
    if py.read_product_id() != Pycoproc.USB_PID_PYSENSE:
        raise Exception('Not a Pysense')
    return py


def get_temperature():
    py = py_connection()
    si = SI7006A20(py)
    return {'temperature': si.temperature()}


def get_humidity():
    py = py_connection()
    si = SI7006A20(py)
    return {'humidity': si.humidity()}


def get_battery_voltage():
    py = py_connection()
    return {'battery_voltage': py.read_battery_voltage()}


def get_pressure():
    py = py_connection()
    press = MPL3115A2(py, mode=PRESSURE)
    return {'pressure': press.pressure()}


def get_battery_percentage():
    py = py_connection()
    # set your battery voltage limits here
    max_value = 4.2
    min_value = 3.3
    battery_voltage = py.read_battery_voltage()
    battery_percentage = (battery_voltage - min_value / (max_value - min_value)) * 100
    return {'battery_percentage': battery_percentage}

def get_acceleration():
    py = py_connection()
    acc = LIS2HH12(py)
    return {'acceleration': acc.acceleration()}

def get_light():
    py = py_connection()
    li = LTR329ALS01(py)
    return {'light': li.light()}