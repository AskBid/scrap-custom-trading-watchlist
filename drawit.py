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

                yClose = 2560, #taken from [-1]
                yOpen = 2556.50, #taken from [-2]
                yLow = 2556.25, #taken from [-2]
                yHigh = 2562.25, #taken from [-2]

                dayOpen = 2560, #taken from [-1]
                price = 2560.75, #taken from [-1]
                dayLow = 2542.5, #taken from [-1]
                dayHigh = 2561.5, #taken from [-1]
                path = "gui/candle.png"):

    def background():
        cr.set_source_rgba(0.4, 0.4, 0.4, 0.5)
        cr.set_line_width(0)
        cr.rectangle(0, 0, thickness, lenght)
        cr.set_line_join(cairo.LINE_JOIN_MITER)
        cr.fill()
        cr.stroke()

    centerY = lenght / 2
    centerX = thickness / 2
    ratio = dayRange / avgRange
    pt2px_rt = 0
    line_w = 2
    arm_len = 3
    deltaOL = dayOpen - dayLow
    deltaOH = price - dayLow

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
    cr = cairo.Context(ims)
    cr.move_to(centerX,centerY)
    cr.scale(1,-1)
    cr.translate(0, -lenght)
    cr.set_line_join(cairo.LINE_CAP_SQUARE)
    background()

    if ratio < 3:
        ## find max points that fit inside canvas
        maxPts = avgRange * 3
        pt2px_rt = lenght / maxPts

    if ratio >= 3:
        maxPts = dayRange
        pt2px_rt = lenght / maxPts

    def pt2px(pts):
        return pts * pt2px_rt

    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0)
    bar_len = pt2px(dayRange)
    half_bar = bar_len / 2
    bar_low = centerY - half_bar
    xBar = centerX + line_w
    cr.set_line_width(line_w)

    #today bar trunk
    cr.rectangle(0, 5, 2, 9)
    cr.rectangle(int(xBar), int(bar_low), int(line_w), int(bar_len))
    # cr.move_to(xBar, bar_low)
    # cr.line_to(xBar, bar_low + bar_len)

    #today arm open
    # cr.rectangle(int(xBar), int(bar_low + pt2px(deltaOL)), int(xBar - arm_len), int(bar_low + pt2px(deltaOL)))
    # cr.move_to(xBar, bar_low + pt2px(deltaOL))
    # cr.line_to(xBar - arm_len, bar_low + pt2px(deltaOL))

    #today arm current/close
    cr.move_to(xBar, bar_low + pt2px(deltaOH))
    cr.line_to(xBar + arm_len, bar_low + pt2px(deltaOH))

    cr.fill()
    cr.stroke()
    ims.write_to_png(path)


if __name__ == "__main__":
    drawCandle()
