# helper functions

import drawSvg

# SVG canvas from physical dimensions and dpi
def canvas_physical(w, h, dpi):
  w_px = w*dpi
  h_px = h*dpi
  return drawSvg.Drawing(w_px, h_px, origin='center', displayInline=False)

# color
