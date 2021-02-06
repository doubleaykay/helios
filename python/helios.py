import numpy
import suncalc # sun library
from datetime import datetime as dt
import pytz

import helper # custom helper functions

year = '2021'

# location
# lat =
# lon =

# get time zone of location
# array of datetimes: (year, [month 1 -> 12], [day 1 -> 31], [hour 00 -> 24], [minute 00 -> 60])
# attach timezone to each datetime object

# IF PRETTY PLOT
# for each datetime, get sun position and color

# IF FUNCTIONAL PLOT
# for each datetime, get sun position and color separating specific sun times

# SVG
# PARAM canvas size
# determine size of minute rectangles
# for each datetime and color, associate with rectangle and plot color
# add axes
# generate and save image PARAM filename
