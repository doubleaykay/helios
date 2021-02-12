from math import pi, tau
from colorsys import hls_to_rgb


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