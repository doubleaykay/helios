from helper import *

# generate using PNG method
year = 2021

# img_title = 'Boston MA'
# lon = -71.0589
# lat = 42.3601

# img_title = 'Koobi Fora'
# lon = 36.1844
# lat = 3.9482

img_title = 'Melbourne'
lon = 144.9631
lat = -37.8136

# img_title = 'Anchorage AK'
# lon = -149.9003
# lat = 61.2181

width = 1920
height = 1080

print('Building array of datetime objects...')
arr_dt = base_date_arr(year)  # naive timestamps as datetime.datetime
print('Converting dates to UTC...')
arr_utc = to_utc(arr_dt, lat, lon, use_dst=True)
print('Calculating sun location and corresponding colors...')
pixels = pos_png(arr_utc, lon, lat, sunrise_jump=0.3, hue_shift=0.0)

print('Generating image...')
gen_png(pixels, width, height, img_title)
