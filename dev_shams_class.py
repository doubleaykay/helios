import numpy as np
import pandas as pd
from math import pi, tau
from typing import Union, Tuple, TextIO

from datetime import datetime, timedelta
import pytz
import timezonefinder
import suncalc

from colorsys import hls_to_rgb
from PIL import Image


class Shams:
    def __init__(self, lon: float, lat: float, start_dt: int, end_dt=None, title: str = 'shams', use_dst: bool = False,
                 sunrise_jump: float = 0.3, hue_shift: float = 0.0):
        self.lon = lon
        self.lat = lat
        self.start_dt = start_dt
        self.end_dt = end_dt if end_dt is not None else start_dt + pd.Timedelta(365, unit='D')
        self.title = title
        self.use_dst = use_dst
        self.sunrise_jump = sunrise_jump
        self.hue_shift = hue_shift

    # generate png from self using specified dimensions
    def gen_png(self, width_px: int = None, height_px: int = None, file_name: str = None, file_pointer: TextIO = None):
        assert file_name is None or file_pointer is None, 'Cannot specify both file_name and file_pointer'

        arr_utc = self._time_arr(self.use_dst)
        azi, alt = self._sun_positions(arr_utc)
        r, g, b = self._get_colors(azi, alt)
        pixels = self._stack_rgb(r, g, b)

        generated_shape = r.shape
        if width_px is None:
            width_px = generated_shape[1]
        if height_px is None:
            height_px = generated_shape[0]

        if file_pointer is None:
            if file_name is None:
                file_name = self.title
            file_name += '.png' * (not file_name.endswith('.png'))
            self._write_png(pixels, width_px, height_px, file_name)
        else:
            self._stream_png(pixels, width_px, height_px, file_pointer)

    def _time_arr(self, use_dst) -> np.ndarray:
        # generate local start and end times
        # localize with derived time zone
        start_time = self.start_dt
        end_time = self.end_dt

        if use_dst:
            # use lat, lon to get local timezone
            tz_str = timezonefinder.TimezoneFinder().certain_timezone_at(lat=self.lat, lng=self.lon)
            try:
                tz = pytz.timezone(tz_str)
            except pytz.exceptions.UnknownTimeZoneError:
                return self._time_arr(use_dst=False)

            # generate times
            times = pd.date_range(start_time, end_time, freq='min') \
                .tz_localize(tz, ambiguous=True, nonexistent=timedelta(days=1))
        else:
            # shift to appropriate 'timezone'
            offset = pd.Timedelta(round(self.lon * 4), unit='min')  # 4 minutes (of time) per degree
            start_time -= offset
            end_time -= offset

            # convert to UTC to capture offset
            start_time = start_time.tz_localize('UTC')
            end_time = end_time.tz_localize('UTC')

            # generate times
            times = pd.date_range(start_time, end_time, freq='min')

        # convert to UTC then python datetime objects in numpy array
        return times.tz_convert('UTC').to_pydatetime()

    # get azimuth and altitude from dates and location
    def _sun_positions(self, arr_utc: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        sc = suncalc.get_position(arr_utc, self.lon, self.lat)
        return sc['azimuth'], sc['altitude']

    # azimuth, altitude to color
    def _get_colors(self, azimuths: np.ndarray, altitudes: np.ndarray) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # ranges from 0 (no jump) to 1 (day is all white, night all black)
        assert 0 <= self.sunrise_jump <= 1, "sunrise_jump must be between 0 and 1 inclusive"

        # can be any float, but values outside the range [0, 1) are redundant
        # shifts all hues in the r -> g -> b -> r direction
        assert isinstance(self.hue_shift, float), "hue_shift must be a float"

        # yes, this could be simplified, and no, don't try to do it please.
        altitude_scaled = (altitudes / pi) * 2  # range [-1, 1]
        altitude_scaled *= 1 - self.sunrise_jump
        idx_alt_pos = altitude_scaled >= 0
        idx_alt_neg = altitude_scaled < 0
        altitude_scaled[idx_alt_pos] += self.sunrise_jump
        altitude_scaled[idx_alt_neg] -= self.sunrise_jump

        hue = ((azimuths / tau) + 0.5 + self.hue_shift) % 1  # range [0, 1]
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

    @staticmethod
    def _stream_png(rgb_arr: np.ndarray, width_px: int, height_px: int, file_pointer: TextIO) -> None:
        Image.fromarray(rgb_arr, mode="RGB") \
            .resize((rgb_arr.shape[1], height_px), Image.BOX) \
            .resize((width_px, height_px), Image.NEAREST) \
            .save(file_pointer)

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, lon: float):
        assert -180 <= lon <= 180, 'lon must be between -180 and 180'
        self._lon = lon

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat: float):
        assert -90 <= lat <= 90, 'lat must be between -90 and 90'
        self._lat = lat

    @property
    def start_dt(self):
        return self._start_dt

    @start_dt.setter
    def start_dt(self, start_dt: Union[int, datetime]):
        if isinstance(start_dt, int):
            self._start_dt = pd.Timestamp(year=start_dt, month=1, day=1)
        else:
            self._start_dt = pd.Timestamp(start_dt).round('D')

    @property
    def end_dt(self):
        return self._end_dt

    @end_dt.setter
    def end_dt(self, end_dt: Union[int, datetime]):
        if isinstance(end_dt, int):
            self._end_dt = pd.Timestamp(year=end_dt, month=1, day=1) - pd.Timedelta(1, unit='min')
        else:
            self._end_dt = pd.Timestamp(end_dt).round('D') - pd.Timedelta(1, unit='min')

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        assert isinstance(title, str), 'title must be a string'
        self._title = title

    @property
    def use_dst(self):
        return self._use_dst

    @use_dst.setter
    def use_dst(self, use_dst: bool):
        assert isinstance(use_dst, bool), 'use_dst must be a bool'
        self._use_dst = use_dst

    @property
    def sunrise_jump(self):
        return self._sunrise_jump

    @sunrise_jump.setter
    def sunrise_jump(self, sunrise_jump: float):
        assert 0 <= sunrise_jump <= 1, 'sunrise_jump must be between 0 and 1'
        self._sunrise_jump = sunrise_jump

    @property
    def hue_shift(self):
        return self._hue_shift

    @hue_shift.setter
    def hue_shift(self, hue_shift: float):
        assert isinstance(hue_shift, float), 'hue_shift must be a float'
        self._hue_shift = hue_shift
