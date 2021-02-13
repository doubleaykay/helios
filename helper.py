from math import pi, tau
from colorsys import hls_to_rgb
from PIL import Image, ImageFilter
import numpy as np
from datetime import datetime
import suncalc


# azimuth, altitude to color
def get_color(azimuth, altitude, sunrise_jump=0.2, hue_shift=0.0, as_hex=True):
    # ranges from 0 (no jump) to 1 (day is all white, night all black)
    assert 0 <= sunrise_jump <= 1, "sunrise_jump must be between 0 and 1 inclusive"

    # can be any float, but values outside the range [0, 1) are redundant
    # shifts all hues in the r -> g -> b -> r direction
    assert isinstance(hue_shift, float), "hue_shift must be a float"

    # yes, this could be simplified, and no, don't try to do it please.
    altitude_scaled = (altitude / pi) * 2  # range [-1, 1]
    altitude_scaled *= 1 - sunrise_jump
    altitude_scaled += sunrise_jump * (1 if altitude >= 0 else -1)  # range [-1, 1]
    lightness = altitude_scaled / 2 + 0.5  # range [0, 1]

    hue = ((azimuth/tau) + 0.5 + hue_shift) % 1  # range [0, 1]

    r, g, b = hls_to_rgb(hue, lightness, 1)
    r = round(255 * r)
    g = round(255 * g)
    b = round(255 * b)
    return "{0:02x}{1:02x}{2:02x}".format(r, g, b).upper() if as_hex else r, g, b


# array of UTC timestamps as np.datetime64 objects
def base_date_arr(year: int, flip: bool, timezone: int = 0):
    assert -12 <= timezone <= 12, f'{timezone} is not a valid timezone shift'

    start_time = np.datetime64(str(year)) - np.timedelta64(timezone, 'h')
    end_time = np.datetime64(str(year+1)) - np.timedelta64(timezone, 'h')

    arr_dt_1d = np.arange(start_time, end_time, dtype='datetime64[m]').astype(datetime)  # 1D array
    arr_dt_2d = arr_dt_1d.reshape(-1, 1440).transpose()  # 2D array with days as columns, time flowing top to bottom

    # flip array along axis 0 since SVG is filled from bottom left corner
    return np.flipud(arr_dt_2d) if flip else arr_dt_2d


# timestamp to sun position to color
# vectorized
def pos_noVec(ts, lon, lat):
    # get sun positions
    azi_alt = suncalc.get_position(ts, lon, lat)
    azi = azi_alt['azimuth']
    alt = azi_alt['altitude']

    # turn positions into colors
    color = get_color(azi, alt)
    return color
    # return pos_to_color(azi, alt) # test first color algorithm
pos = np.vectorize(pos_noVec)


# color hex codes to svg
def gen_svg(colors, d, width, height, x_tick, y_tick):
    # index tuple is (y,x)
    # # x is the axis 1 index
    # y is the axis 0 index

    it = np.nditer(colors, flags=['multi_index'])  # keep track of index
    for color in it:
        y = it.multi_index[0] * y_tick  # get y position
        x = it.multi_index[1] * x_tick  # get x position
        r = draw.Rectangle(x, y, x_tick, y_tick, fill=f'#{color}', stroke_width=0)  # create rectangle
        d.append(r)  # draw rectangle on canvas


# timestamp to sun position to rgb color
# for png method
def pos_png(arr_dt, lon, lat, sunrise_jump=0.0, hue_shift=0.0):
    # get shape of old array
    shape_old = arr_dt.shape
    # create empty array with old shape and depth 3
    rgb_arr = np.empty((shape_old[0], shape_old[1], 3), dtype=np.uint8)

    for row_idx in range(shape_old[0]):
        for col_idx in range(shape_old[1]):
            azi_alt = suncalc.get_position(arr_dt[row_idx, col_idx], lon, lat)
            r, g, b = get_color(azi_alt['azimuth'], azi_alt['altitude'],
                                sunrise_jump=sunrise_jump, hue_shift=hue_shift, as_hex=False)
            rgb_arr[row_idx, col_idx, 0] = r
            rgb_arr[row_idx, col_idx, 1] = g
            rgb_arr[row_idx, col_idx, 2] = b

    return rgb_arr


# generate PNG using pixel data
def gen_png(rgb_arr, width, height, file_name):
    Image.fromarray(rgb_arr, mode="RGB") \
        .resize((rgb_arr.shape[1], height), Image.BOX)\
        .resize((width, height), Image.NEAREST)\
        .save(file_name + '.png')
