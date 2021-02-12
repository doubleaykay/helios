"""
Generate pretty plot of sun position for given year, lat, lon.

Written by Anoush Khan & Dan Strauss
February 2021
"""
import numpy as np
import suncalc
import drawSvg as draw
from datetime import datetime

# import to test first color algorithm
# from test_color import *

# array of timestamps
def base_date_arr(year):
    # get all days in year
    days = np.arange(str(year), str(year+1), dtype='datetime64[D]')

    # get minutes in each day as row vector
    lst = []
    for day in days:
        lst.append(np.arange(day, day+1, dtype='datetime64[m]'))

    # construct np.array
    lst_arr = np.array(lst)
    # transpose to get minutes as column vectors
    arr_dt64_noflip = lst_arr.T
    # flip array along axis 0 since SVG is filled from bottom left corner
    arr_dt64 = np.flip(arr_dt64_noflip, axis=0)
    
    return arr_dt64

# convert from array of datetime64 to normal datetime with the UTC timestamp attached
# vectorized
def dt64_to_dtUTC_noVec(dt64):
    dt64 = np.datetime64(dt64) # correct dtype
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
    color = dan_color(azi, alt) # DAN!!
    return color
    # return pos_to_color(azi, alt) # test first color algorithm
pos = np.vectorize(pos_noVec)

# color hex codes to svg
def gen_svg(colors, d, width, height, x_tick, y_tick):
    # index tuple is (y,x)
    # # x is the axis 1 index
    # y is the axis 0 index
    
    it = np.nditer(colors, flags=['multi_index']) # keep track of index
    for color in it:
        y = it.multi_index[0] * y_tick # get y position
        x = it.multi_index[1] * x_tick # get x position
        r = draw.Rectangle(x, y, x_tick, y_tick, fill=f'#{color}') # create rectangle
        d.append(r) # draw rectangle on canvas

# main function
def let_there_be_light(year, lon, lat, width, height, outfile):
    # times to sun positions to colors
    arr_dt64 = base_date_arr(year) # numpy timestamps
    arr_dtUTC = dt64_to_dtUTC(arr_dt64) # UTC timestamps
    colored = pos(arr_dtUTC, lon, lat) # hex code colors

    # svg parameters
    x_tick = width / 365 # days in a year
    y_tick = height / 1440 # min in a day

    # svg canvas
    d = draw.Drawing(width, height, displayInline=False)

    # generate svg
    gen_svg(colored, d, width, height, x_tick, y_tick)

    # save svg
    d.setPixelScale(2)
    d.savePng(outfile)

    print('Done.')

if __name__ == "__main__":
    # params
    # TTD get these from command line or interface
    year = 2021
    lon = 71.0589
    lat = 42.3601
    width = 1920
    height = 1080
    outfile = 'color_test2.png'

    let_there_be_light(year, lon, lat, width, height, outfile)