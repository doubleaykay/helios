# import numpy as np
# import suncalc
import drawSvg as draw
# from datetime import datetime

from helper import *


# main function
def let_there_be_light(year, lon, lat, width, height, outfile):
    # times to sun positions to colors
    arr_dt = base_date_arr(year, flip=False)  # UTC timestamps
    colored = pos_svg(arr_dt, lon, lat)  # hex code colors

    # svg parameters
    x_tick = width / 365  # days in a year
    y_tick = height / 1440  # min in a day

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
    # lon = 71.0589
    # lat = 42.3601
    lon = -71.0589
    lat = 42.3601
    width = 1920
    height = 1080
    outfile = 'color_test6.png'

    let_there_be_light(year, lon, lat, width, height, outfile)