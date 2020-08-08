from enum import Enum


class ATC_RESPONSE(Enum):
    GRANTED = 1,
    DENIED = 2,
    STANDBY = 3,
    ACKNOWLEDGE = 4


class FLIGHT_STATE(Enum):
    TAXI = 1,
    HOLD_SHORT_RUNWAY = 2,
    TAKE_RUNWAY = 3,
    TAKEOFF = 4,
    INBOUND = 5,
    INITIAL = 6,
    FINAL = 7,
    CLEAR_RUNWAY = 8,
    DEPART_RUNWAY = 9,
    UNKNOWN = 10,
    NEW = 11,
    WAIT_FOR_TAXI = 12

class AIRCRAFT(Enum):
    HORNET = 1,
    VIPER = 2,
    TOMCAT = 3,
    HARRIER = 4,
    HAWG = 5,
    UNKNOWN = 6