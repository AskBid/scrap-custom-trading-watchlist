try:
    import cairo
except:
    pass
try:
    import cairocffi as cairo
except:
    pass
from math import radians
from math import isnan

def draw52RangeBar(lenght = 226,
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

def drawCandle( lenght = 200, thickness = 25,

                avgRange = 10.17,
                stdRange = 4.0235,
                dayRange = 19,

                yClose = 2557, #taken from [-1]
                yOpen = 2556.50, #taken from [-2]
                yLow = 2556.25, #taken from [-2]
                yHigh = 2562.25, #taken from [-2]

                dayOpen = 2560, #taken from [-1]
                price = 2550.75, #taken from [-1]
                dayLow = 2542.5, #taken from [-1]

                path = "gui/candle.png",
                type_="bar"):

    def background(r,g,b):
        cr.set_source_rgb(r, g, b)
        cr.set_line_width(0)
        cr.rectangle(0, 0, thickness, lenght)
        cr.set_line_join(cairo.LINE_JOIN_MITER)
        cr.fill()
        cr.stroke()

    values = (avgRange, stdRange, dayRange, yClose, yOpen, yLow, yHigh, dayOpen, price, dayLow)
    for value in values:
        if isnan(value):
            ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
            cr = cairo.Context(ims)
            background(1,0,0)
            ims.write_to_png(path)
            return 'NaN'

    centerY = lenght / 2

    space_border = 5
    space_bars = 1
    trunk_w = 3
    arm_line_w = 2
    half_arm_line_w = 1
    arm_len = 1
    body_w = 4

    thickness = space_border + (trunk_w * 6)

    pt2px_rt = 0
    ratio = dayRange / avgRange

    deltaOL = dayOpen - dayLow
    deltaPL = price - dayLow
    deltaLows =  yLow - dayLow
    deltaOL_y = yOpen - yLow
    deltaPL_y = yClose - yLow

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
    cr = cairo.Context(ims)
    cr.move_to(0,centerY)
    cr.scale(1,-1)
    cr.translate(0, -lenght)
    cr.set_line_join(cairo.LINE_CAP_SQUARE)
    background(0.95,0.95,0.95)

    if ratio < 2:
        ## find max points that fit inside canvas
        maxPts = avgRange * 3
        pt2px_rt = lenght / maxPts

    if ratio >= 2:
        ## find max points that fit inside canvas
        maxPts = dayRange * 2
        pt2px_rt = lenght / maxPts

    def pt2px(pts):
        return pts * pt2px_rt

    def bar(x_start, y_start, len_LH, len_O, len_P, type_func, a):
        def arms():
            #today arm open
            cr.rectangle(int(x_start),
                         int(y_start + len_O - half_arm_line_w),
                         int(-arm_len),
                         int(arm_line_w))
            #today arm current/close
            cr.rectangle(int(x_start + trunk_w),
                         int(y_start + len_P - half_arm_line_w),
                         int(arm_len),
                         int(arm_line_w))
            cr.fill()

        if len_O < len_P:
            cr.set_source_rgba(0.1, 0.8, 0.35,a)
        else:
            cr.set_source_rgba(1, 0.29, 0.3,a)
        cr.set_line_width(0)

        arms()

        cr.rectangle(int(x_start),
                     int(y_start),
                     int(trunk_w),
                     int(len_LH))
        cr.fill()

    def avg_std_box(y_start, avg, std):

        cr.set_source_rgba(0.2, 0.2, 0.2, 0.1)
        cr.set_line_width(0)

        avg = int(avg)

        cr.rectangle(0,
                     int(y_start),
                     thickness,
                     avg)
        cr.fill()

        if ratio >= 2:
            for i in range(0,10):
                cr.set_source_rgba(0.3, 0.3, 0.3, 0.1)
                cr.rectangle(0,
                             int(y_start - (avg * 2) + (avg * i)),
                             thickness,
                             2)
                cr.fill()

        cr.set_source_rgba(0, 0, 0.2, 0.1)

        for i in range(0,thickness,2):
            cr.rectangle(0 + i,
                         int(y_start + avg - std),
                         1,
                         int(std*2))
            cr.fill()


    bar_len = pt2px(dayRange)
    bar_low = int(lenght / 3)
    bar_low_y = bar_low + pt2px(deltaLows)
    bar_len_y = pt2px(yHigh - yLow)

    avg_std_box(bar_low, pt2px(avgRange), pt2px(stdRange))

    bar(space_border + arm_len,
        bar_low_y,
        bar_len_y,
        pt2px(deltaOL_y),
        pt2px(deltaPL_y),
        type_,
        0.5)

    bar(space_border + (arm_len*3) + trunk_w + space_bars,
        bar_low,
        bar_len,
        pt2px(deltaOL),
        pt2px(deltaPL),
        type_,
        0.9)

    ims.write_to_png(path)


if __name__ == "__main__":
    drawCandle()
