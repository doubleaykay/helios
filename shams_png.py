from helper import *

# generate using PNG method
year = 2021

lon = -71.0589
lat = 42.3601
width = 1920
height = 1080

x_tick = round(width / 365)  # days in a year
y_tick = round(height / 1440)  # min in a day

arr_dt64 = base_date_arr(year, flip=False)  # numpy timestamps
arr_dtUTC = dt64_to_dtUTC(arr_dt64)  # UTC timestamps
arr_tiled = broadcast_tile(arr_dtUTC, y_tick, x_tick)

colored = pos_png(arr_tiled, lon, lat)
gen_png(colored, 'test.png')