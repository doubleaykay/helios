import math
from colorsys import hls_to_rgb

# azimuth, altitude to color
def get_color(azimuth, altitude):
    # adjust this to taste or make it an input. Ranges from 0 (no jump) to 1 (day is all white, night all black)
    sunrise_jump = 0.3
    assert 0 <= sunrise_jump <= 1, "sunrise_jump must be between 0 and 1 inclusive"

    # yes, this could be simplified, and no, don't try to do it please.
    altitude_scaled = (altitude / math.pi) * 2  # range [-1, 1]
    altitude_scaled *= 1 - sunrise_jump
    altitude_scaled += sunrise_jump if (altitude >= 0) else -sunrise_jump  # range []
    altitude_scaled /= 2
    altitude_scaled += 0.5  # range [0, 1]

    azimuth_scaled = (azimuth/math.tau) + 0.5  # range [0, 1]

    r, g, b = hls_to_rgb(azimuth_scaled, altitude_scaled, 1)
    r = round(255 * r)
    g = round(255 * g)
    b = round(255 * b)
    return "{0:02x}{1:02x}{2:02x}".format(r, g, b).upper()