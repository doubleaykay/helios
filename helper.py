import numpy as np
from math import pi, tau

from datetime import datetime, timezone
from tzwhere import tzwhere
import pytz
import suncalc

from colorsys import hls_to_rgb
from PIL import Image
import drawSvg as draw


# azimuth, altitude to color
def get_color(azimuth, altitude, sunrise_jump=0.2, hue_shift=0.0):
    # ranges from 0 (no jump) to 1 (day is all white, night all black)
    assert 0 <= sunrise_jump <= 1, "sunrise_jump must be between 0 and 1 inclusive"

    # can be any float, but values outside the range [0, 1) are redundant
    # shifts all hues in the r -> g -> b -> r direction
    assert isinstance(hue_shift, float), "hue_shift must be a float"

    # yes, this could be simplified, and no, don't try to do it please.
    altitude_scaled = (altitude / pi) * 2  # range [-1, 1]
    altitude_scaled *= 1 - sunrise_jump
    idx_alt_pos = altitude_scaled >= 0
    idx_alt_neg = altitude_scaled < 0
    altitude_scaled[idx_alt_pos] += sunrise_jump
    altitude_scaled[idx_alt_neg] -= sunrise_jump
    lightness = altitude_scaled / 2 + 0.5  # range [0, 1]

    hue = ((azimuth / tau) + 0.5 + hue_shift) % 1  # range [0, 1]
    
    saturation = np.ones(hue.shape)
    
    r, g, b = np.vectorize(hls_to_rgb)(hue, lightness, saturation)
    
    r = np.round(255 * r)
    g = np.round(255 * g)
    b = np.round(255 * b)
    
    return r, g, b


# array of UTC timestamps as naive datetime objects
def base_date_arr(year: int):
    start_time = np.datetime64(str(year))
    end_time = np.datetime64(str(year + 1))

    arr_dt_1d = np.arange(start_time, end_time, dtype='datetime64[m]').astype(datetime)  # 1D array

    return arr_dt_1d


# array of naive timestamps to array of time zone aware timestamps
def to_utc(arr, lon, lat, use_dst: bool):
    tz_str = tzwhere.tzwhere().tzNameAt(lon, lat)
    tz = pytz.timezone(tz_str)

    def one_dt_utc(dt):
        return (dt - offset).replace(tzinfo=timezone.utc)

    def one_dt_localized(dt):
        return tz.localize(dt).astimezone(pytz.utc)

    if use_dst:
        return np.vectorize(one_dt_localized)(arr)
    else:
        # offset = tz.utcoffset(arr[0, 0], is_dst=False)
        offset = tz.utcoffset(arr[0], is_dst=False)
        return np.vectorize(one_dt_utc)(arr)


# array of timestamps to sun positions, then to [r, g, b]]
# def pos_png(arr_dt, lon, lat, sunrise_jump=0.0, hue_shift=0.0):
#     # get shape of input array
#     shape_old = arr_dt.shape
#     # create empty array with old shape and depth 3
#     rgb_arr = np.empty((shape_old[0], shape_old[1], 3), dtype=np.uint8)

#     for row_idx in range(shape_old[0]):
#         for col_idx in range(shape_old[1]):
#             azi_alt = suncalc.get_position(arr_dt[row_idx, col_idx], lon, lat)
#             r, g, b = get_color(azi_alt['azimuth'], azi_alt['altitude'],
#                                 sunrise_jump=sunrise_jump, hue_shift=hue_shift, as_hex=False)
#             rgb_arr[row_idx, col_idx, 0] = r
#             rgb_arr[row_idx, col_idx, 1] = g
#             rgb_arr[row_idx, col_idx, 2] = b

#     return rgb_arr


# stack RGB elements into 3d pixel array
def stack_rgb(r, g, b):
    new = np.empty((1440,365,3), dtype=np.uint8)
    new[:,:,0] = r.reshape((-1,1440)).T
    new[:,:,1] = g.reshape((-1,1440)).T
    new[:,:,2] = b.reshape((-1,1440)).T
    return new


# generate PNG using pixel data
def gen_png(rgb_arr, width, height, file_name):
    if '.png' not in file_name: file_name = file_name + '.png'
    Image.fromarray(rgb_arr, mode="RGB") \
        .resize((rgb_arr.shape[1], height), Image.BOX) \
        .resize((width, height), Image.NEAREST) \
        .save(file_name)