from math import pi, tau
from colorsys import hls_to_rgb
import png
import numpy as np
from datetime import datetime
import suncalc


# azimuth, altitude to color
def get_color(azimuth, altitude, sunrise_jump=0.2, hue_shift=0, as_hex=True):
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


# array of timestamps
def base_date_arr(year, flip):
    # get all days in year
    days = np.arange(str(year), str(year + 1), dtype='datetime64[D]')

    # get minutes in each day as row vector
    lst = []
    for day in days:
        lst.append(np.arange(day, day + 1, dtype='datetime64[m]'))

    # construct np.array
    lst_arr = np.array(lst)
    # transpose to get minutes as column vectors
    arr_dt64_noflip = lst_arr.T
    # flip array along axis 0 since SVG is filled from bottom left corner
    # arr_dt64 = np.flip(arr_dt64_noflip, axis=0)
    # arr_dt64 = arr_dt64_noflip

    return np.flip(arr_dt64_noflip, axis=0) if flip else arr_dt64_noflip

    # return arr_dt64


# convert from array of datetime64 to normal datetime with the UTC timestamp attached
# vectorized
def dt64_to_dtUTC_noVec(dt64):
    dt64 = np.datetime64(dt64)  # correct dtype
    ts = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    return datetime.utcfromtimestamp(ts)
dt64_to_dtUTC = np.vectorize(dt64_to_dtUTC_noVec)


# timestamp to sun position to color
# vectorized
def pos_noVec(ts, lon, lat):
    # get sun positions
    azi_alt = suncalc.get_position(ts, lon, lat)
    azi = azi_alt['azimuth']
    alt = azi_alt['altitude']

    # turn positions into colors
    color = get_color(azi, alt)  # DAAAAAAAN!!
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


# tile each element
# for PNG method
def broadcast_tile(a, h, w):
    # from https://stackoverflow.com/a/52346065
    x, y = a.shape
    m, n = x * h, y * w
    return np.broadcast_to(
        a.reshape(x, 1, y, 1), (x, h, y, w)
    ).reshape(m, n)

# timestamp to sun position to rgb color
# for png method
def pos_png(arr, lon, lat):
    # get shape of old array
    shape_old = arr.shape
    # create empty array with old shape and depth 3
    new_arr = np.empty((shape_old[0], shape_old[1], 3), dtype=np.uint8)

    # print(type(arr[0,0]))

    # iterate over every element in old array
    it = np.nditer(arr, flags=['multi_index', 'refs_ok'])
    for itm in it:
        r_idx = (it.multi_index[0], it.multi_index[1], 0)
        g_idx = (it.multi_index[0], it.multi_index[1], 1)
        b_idx = (it.multi_index[0], it.multi_index[1], 2)

        # print(type(itm[0]))

        # get sun position
        azi_alt = suncalc.get_position(itm.item(), lon, lat)
        azi = azi_alt['azimuth']
        alt = azi_alt['altitude']

        # get color from position
        rgb = get_color(azi, alt, sunrise_jump=0.2, hue_shift=0.0, as_hex=False)

        # place rgb values in correct place
        new_arr[r_idx] = rgb[0]
        new_arr[g_idx] = rgb[1]
        new_arr[b_idx] = rgb[2]

    # flatten 3d array into 2d
    new_lst2 = []
    for row in new_arr:
        new_lst2.append(row.flatten())

    new_new_arr = np.array(new_lst2)

    return new_new_arr


# generate PNG using pixel data
def gen_png(rgb_arr, fname):
    png.from_array(rgb_arr, 'rgb').save(fname)