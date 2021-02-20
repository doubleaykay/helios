from helper import *

# img_title = 'Boston, MA'
# lon = -71.0589
# lat = 42.3601

# img_title = 'Koobi Fora, Kenya'
# lon = 36.1844
# lat = 3.9482

# img_title = 'Melbourne, Australia'
# lon = 144.9631
# lat = -37.8136

# img_title = 'Anchorage, AK'
# lon = -149.9003
# lat = 61.2181

# img_title = 'Lahore, Pakistan'
# lon = 74.329376
# lat = 31.582045

# img_title = 'Singapore'
# lon = 103.851959
# lat = 1.290270

# img_title = 'Base Marambio, Antarctica'
# lat = -64.25149364250075
# lon = -56.65526998841897

img_title = 'Reykjavik'
lat = 64.128288
lon = -21.827774

year = 2021

use_dst = True

sunrise_jump = 0.3
hue_shift = 0.0

width_px = 1920
height_px = 1080

# bef = datetime.now()

arr_utc = time_arr(year, lon, lat, use_dst=use_dst)
azi, alt = sun_positions(arr_utc, lon, lat)
r, g, b = get_colors(azi, alt, sunrise_jump=sunrise_jump, hue_shift=hue_shift)
pixels = stack_rgb(r, g, b)
gen_png(pixels, width_px, height_px, img_title)

# af = datetime.now() - bef
# print(f'Took {af}')

