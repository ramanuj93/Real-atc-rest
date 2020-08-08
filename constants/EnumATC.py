from enum import Enum


class ATC_RESPONSE(Enum):
    GRANTED = 1,
    DENIED = 2,
    STANDBY = 3,
    ACKNOWLEDGE = 4,
    UNCLEAR = 5


class FLIGHT_STATE(Enum):
    TAXI = 1,
    TAXI_HOLD = 2,
    HOLD_SHORT_RUNWAY = 3,
    TAKE_RUNWAY = 4,
    TAKEOFF = 5,
    INBOUND = 6,
    INITIAL = 7,
    FINAL = 8,
    CLEAR_RUNWAY = 9,
    DEPART_RUNWAY = 10,
    UNKNOWN = 11,
    NEW = 12,
    WAIT_FOR_TAXI = 13


class AIRCRAFT(Enum):
    HORNET = 1,
    VIPER = 2,
    TOMCAT = 3,
    HARRIER = 4,
    HAWG = 5,
    UNKNOWN = 6