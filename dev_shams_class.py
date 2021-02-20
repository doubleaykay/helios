import numpy as np
import pandas as pd
from math import pi, tau
from typing import Tuple

from datetime import datetime, timedelta
import pytz
import timezonefinder
import suncalc

from colorsys import hls_to_rgb
from PIL import Image


class Shams:
    def __init__(self, lon: float, lat: float, year: int, title: str = 'shams',
                 use_dst: bool = False, sunrise_jump: float = 0.3, hue_shift: float = 0.0):
        self._lon = lon
        self._lat = lat
        self._year = year
        self._title = title
        self._use_dst = use_dst
        self._sunrise_jump = sunrise_jump
        self._hue_shift = hue_shift

    def gen_png(self, width_px, height_px, file_name: str = None):
        if file_name is None:
            file_name = self._title
        if file_name[-4:] != '.png':
            file_name = file_name + '.png'
        arr_utc = self._time_arr()
        azi, alt = self._sun_positions(arr_utc)
        r, g, b = self._get_colors(azi, alt)
        pixels = self._stack_rgb(r, g, b)
        self._write_png(pixels, width_px, height_px, file_name)

    def _time_arr(self) -> np.ndarray:
        # determine timezone based on lon, lat
        tz_str = timezonefinder.TimezoneFinder().certain_timezone_at(lat=self._lat, lng=self._lon)
        tz = pytz.timezone(tz_str)

        # generate local start and end times
        # localize with derived time zone
        start_time = pd.to_datetime(datetime(self._year, 1, 1))
        end_time = pd.to_datetime(datetime(self._year, 12, 31, 23, 59))

        if self._use_dst:
            # generate times
            times = pd.date_range(start_time, end_time, freq='min') \
                .tz_localize(tz, ambiguous=True, nonexistent=timedelta(days=1))
        else:
            # convert to UTC to capture offset
            start_time = start_time.tz_localize(tz).tz_convert('UTC')
            end_time = end_time.tz_localize(tz).tz_convert('UTC')

            # generate times
            times = pd.date_range(start_time, end_time, freq='min')

        # convert to UTC then python datetime objects in numpy array
        return times.tz_convert('UTC').to_pydatetime()

    # get azimuth and altitude from dates and location
    def _sun_positions(self, arr_utc: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        sc = suncalc.get_position(arr_utc, self._lon, self._lat)
        return sc['azimuth'], sc['altitude']

    # azimuth, altitude to color
    def _get_colors(self, azimuths: np.ndarray, altitudes: np.ndarray) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # ranges from 0 (no jump) to 1 (day is all white, night all black)
        assert 0 <= self._sunrise_jump <= 1, "sunrise_jump must be between 0 and 1 inclusive"

        # can be any float, but values outside the range [0, 1) are redundant
        # shifts all hues in the r -> g -> b -> r direction
        assert isinstance(self._hue_shift, float), "hue_shift must be a float"

        # yes, this could be simplified, and no, don't try to do it please.
        altitude_scaled = (altitudes / pi) * 2  # range [-1, 1]
        altitude_scaled *= 1 - self._sunrise_jump
        idx_alt_pos = altitude_scaled >= 0
        idx_alt_neg = altitude_scaled < 0
        altitude_scaled[idx_alt_pos] += self._sunrise_jump
        altitude_scaled[idx_alt_neg] -= self._sunrise_jump

        hue = ((azimuths / tau) + 0.5 + self._hue_shift) % 1  # range [0, 1]
        lightness = altitude_scaled / 2 + 0.5  # range [0, 1]
        saturation = np.ones(hue.shape)  # range [1, 1]

        r, g, b = np.vectorize(hls_to_rgb)(hue, lightness, saturation)

        r = np.round(255 * r)
        g = np.round(255 * g)
        b = np.round(255 * b)

        return r, g, b

    # stack RGB elements into 3d pixel array
    @staticmethod
    def _stack_rgb(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
        width = int(len(r) / 1440)  # in case of leap year
        new = np.empty((1440, width, 3), dtype=np.uint8)
        new[:, :, 0] = r.reshape((-1, 1440)).T
        new[:, :, 1] = g.reshape((-1, 1440)).T
        new[:, :, 2] = b.reshape((-1, 1440)).T
        return new

    # generate PNG using pixel data
    @staticmethod
    def _write_png(rgb_arr: np.ndarray, width_px: int, height_px: int, file_name) -> None:
        Image.fromarray(rgb_arr, mode="RGB") \
            .resize((rgb_arr.shape[1], height_px), Image.BOX) \
            .resize((width_px, height_px), Image.NEAREST) \
            .save(file_name)

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, lon):
        assert -180 <= lon <= 180, 'lon must be between -180 and 180'
        self._lon = lon

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        assert -90 <= lat <= 90, 'lat must be between -90 and 90'
        self._lon = lat

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        assert isinstance(year, int), 'year must be an integer'
        self._year = year

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        assert isinstance(title, str), 'title must be a string'
        self._title = title

    @property
    def use_dst(self):
        return self._use_dst

    @use_dst.setter
    def use_dst(self, use_dst):
        assert isinstance(use_dst, bool), 'use_dst must be a bool'
        self._use_dst = use_dst

    @property
    def sunrise_jump(self):
        return self._sunrise_jump

    @sunrise_jump.setter
    def sunrise_jump(self, sunrise_jump):
        assert 0 <= sunrise_jump <= 1, 'sunrise_jump must be between 0 and 1'
        self._sunrise_jump = sunrise_jump

    @property
    def hue_shift(self):
        return self._hue_shift

    @hue_shift.setter
    def hue_shift(self, hue_shift):
        assert isinstance(hue_shift, float), 'hue_shift must be a float'
        self._hue_shift = hue_shift
