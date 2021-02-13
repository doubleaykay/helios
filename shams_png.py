from helper import *

# generate using PNG method
year = 2021

lon = -71.0589
lat = 42.3601
timezone = 0  # shift from UTC, e.g. -5 for Boston. Leave at 0 until we fix suncalc timezone B.S.

width = 1920
height = 1080

print('Building array of datetime objects...')
arr_dt_utc = base_date_arr(year, flip=True, timezone=timezone)  # UTC timestamps as datetime.datetime
print('Calculating sun location and corresponding colors...')
pixels = pos_png(arr_dt_utc, lon, lat, sunrise_jump=0.3, hue_shift=0.0)

print('Generating image...')
gen_png(pixels, width, height, 'Boston')
