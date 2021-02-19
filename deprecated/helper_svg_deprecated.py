
# array of timestamps to sun position, then to hex color
def pos_svg(arr_dt, lon, lat, sunrise_jump=0.0, hue_shift=0.0):

    # get shape of input array
    shape_old = arr_dt.shape
    # create empty array with old shape and depth 3
    rgb_arr = np.empty(shape_old, dtype=np.str_)

    for row_idx in range(shape_old[0]):
        for col_idx in range(shape_old[1]):
            azi_alt = suncalc.get_position(arr_dt[row_idx, col_idx], lon, lat)
            rgb_arr[row_idx, col_idx] = get_color(azi_alt['azimuth'], azi_alt['altitude'],
                                                  sunrise_jump=sunrise_jump, hue_shift=hue_shift, as_hex=True)
    return rgb_arr


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