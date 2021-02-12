import colorsys
import numpy as np

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # from https://stackoverflow.com/a/1969274
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def pos_to_color(azi, alt):
    # lumosity = angle from horizon = altitude
    # hue = angle from north = azimuth
    s = 100 / 100
    
    # l from 0 to 100
    # h from 0 to 360
    
    h = translate(azi, -1*np.pi, np.pi, 0, 360)
    l = translate(alt, -1*np.pi/2, np.pi/2, 0, 100) / 100
    
    # from https://stackoverflow.com/a/24852375
    def hsv2rgb(h,l,s):
        return tuple(round(i * 255) for i in colorsys.hls_to_rgb(h,l,s))
    
    # rgb = colorsys.hls_to_rgb(h, l, s)
    rgb = hsv2rgb(h, l, s)
    
    # from https://stackoverflow.com/a/3380739
    return '%02x%02x%02x' % rgb
    # return str((np.rint(h), np.rint(l), np.rint(s)))
    # return(str(rgb))