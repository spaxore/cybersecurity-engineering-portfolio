import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gps_parser import get_gps_coordinates, _dms_to_decimal


class FakeRatio:
    def __init__(self, num, den):
        self.num = num
        self.den = den


class FakeTag:
    def __init__(self, values):
        self.values = values

    def __str__(self):
        return self._str_value

    def set_str(self, s):
        self._str_value = s
        return self


def test_dms_to_decimal_known_value():
    # 48 degrees, 51 minutes, 24 seconds ~= 48.8567 decimal
    values = [FakeRatio(48, 1), FakeRatio(51, 1), FakeRatio(24, 1)]
    result = _dms_to_decimal(values)
    assert round(result, 4) == 48.8567


def test_get_gps_coordinates_north_east():
    tags = {
        "GPS GPSLatitude": FakeTag([FakeRatio(48, 1), FakeRatio(51, 1), FakeRatio(24, 1)]),
        "GPS GPSLatitudeRef": FakeTag([]).set_str("N"),
        "GPS GPSLongitude": FakeTag([FakeRatio(2, 1), FakeRatio(21, 1), FakeRatio(3, 1)]),
        "GPS GPSLongitudeRef": FakeTag([]).set_str("E"),
    }
    lat, lon = get_gps_coordinates(tags)
    assert lat > 0
    assert lon > 0


def test_get_gps_coordinates_south_west_are_negative():
    tags = {
        "GPS GPSLatitude": FakeTag([FakeRatio(23, 1), FakeRatio(33, 1), FakeRatio(0, 1)]),
        "GPS GPSLatitudeRef": FakeTag([]).set_str("S"),
        "GPS GPSLongitude": FakeTag([FakeRatio(46, 1), FakeRatio(38, 1), FakeRatio(0, 1)]),
        "GPS GPSLongitudeRef": FakeTag([]).set_str("W"),
    }
    lat, lon = get_gps_coordinates(tags)
    assert lat < 0
    assert lon < 0


def test_no_gps_tags_returns_none():
    tags = {"Image Model": FakeTag([]).set_str("iPhone 13")}
    assert get_gps_coordinates(tags) is None
