from helper import *

# generate using PNG method

# img_title = 'Boston MA'
# lon = -71.0589
# lat = 42.3601

# img_title = 'Boston MA NO DST'
# lon = -71.0589
# lat = 42.3601

# img_title = 'Koobi Fora'
# lon = 36.1844
# lat = 3.9482

# img_title = 'Melbourne'
# lon = 144.9631
# lat = -37.8136

# img_title = 'Anchorage AK NO_DST'
# lon = -149.9003
# lat = 61.2181

img_title = 'Lahore PK 2020'
lon = 74.329376
lat = 31.582045

year = 2020

use_dst = False

sunrise_jump = 0.3
hue_shift = 0.0

width = 1920
height = 1080

# bef = datetime.now()

arr_utc = time_arr(year, lon, lat, use_dst=use_dst)
sc = suncalc.get_position(arr_utc, lon, lat)
r, g, b = get_color(sc['azimuth'], sc['altitude'], sunrise_jump=sunrise_jump, hue_shift=hue_shift)
pixels = stack_rgb(r, g, b)
gen_png(pixels, width, height, img_title)

# af = datetime.now() - bef
# print(f'Took {af}')

