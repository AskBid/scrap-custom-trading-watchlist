try:
    import cairo
except:
    pass
try:
    import cairocffi as cairo
except:
    pass
from math import radians

def drawBar(lenght = 226,
            thickness = 6,
            low52 = 11865.0,
            range52 = 1070.5, #12935.5  high52
            dopen = 12527.00, #day open
            drange = 157.50,
            path = "gui/bar_trial.png",
            orientation = "Vertical"):

    left2open_px = (lenght / range52) * (dopen - low52)
    range_px = (lenght / range52) * drange

    if orientation == 'Vertical':
        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
        cr = cairo.Context(ims)
        cr.translate(0, lenght)
        cr.move_to(0,0)
        cr.rotate(radians(-90))
    else:
        ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, lenght, thickness)
        cr = cairo.Context(ims)

    cr.set_line_width(0)
    cr.set_source_rgb(0, 0, 0)
    cr.rectangle(0, 0, lenght, thickness)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()

    cr.set_source_rgb(1, 1, 1)

    if left2open_px > (lenght - 3):
        left2open_px = lenght - 3
        cr.rectangle(left2open_px, 2, range_px, 2)

    if range_px < 3:
        range_px = 3


    cr.rectangle(left2open_px, 0, range_px, thickness)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()

    ims.write_to_png(path)

def drawCandle( lenght = 226,
                thickness = 15,

                avgRange = 10.17,
                dayRange = 19,

                yClose = 2560, #12935.5  52rH
                yOpen = 2556,
                yLow = 2556.25,
                yHigh = 2562.25,

                dayOpen = 2560, #day open
                dayClose = 2560.75,
                dayLow = 2542.5,
                dayHigh = 2561.5,
                path = "gui/candle.png"):

    centerY = lenght / 2
    centerX = thickness / 2
    ratio = dayRange / avgRange
    pts2pxs_rt = 0

    if ratio < 3:
        ## find max points that fit inside canvas
        maxPts = avgRange * 3
        pts2pxs_rt = lenght / maxPts

    if ratio >= 3:
        maxPts = dayRange
        pts2pxs_rt = lenght / maxPts

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
    cr = cairo.Context(ims)
    cr.move_to(centerX,centerY)
    cr.scale(1,-1)
    cr.translate(0, -lenght)

    cr.set_source_rgba(0.4, 0.4, 0.4, 0.5)
    cr.set_line_width(0)
    cr.rectangle(0, 0, thickness, lenght)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()

    def pts2px(max_L):
        pass

    def lineByCenter(bar_len):
        half_bar = bar_len / 2
        start = centerY - half_bar

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(2)

        cr.move_to(centerX, start)
        cr.line_to(centerX, start + bar_len)
        cr.stroke()

    drawLineCenter(16)

    ratio = dayRange / avgRange


    ims.write_to_png(path)

if __name__ == "__main__":
    drawCandle()
