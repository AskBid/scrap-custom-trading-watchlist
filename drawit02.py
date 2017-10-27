try:
    import cairo
except:
    pass
try:
    import cairocffi as cairo
except:
    pass
from math import radians

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

                yClose = 2560, #taken from [-1]
                yOpen = 2556.50, #taken from [-2]
                yLow = 2556.25, #taken from [-2]
                yHigh = 2562.25, #taken from [-2]

                dayOpen = 2560, #taken from [-1]
                price = 2560.75, #taken from [-1]
                dayLow = 2542.5, #taken from [-1]

                path = "gui/candle.png",
                type_="bar"):

    def background():
        cr.set_source_rgba(0.4, 0.4, 0.4, 0.5)
        cr.set_line_width(0)
        cr.rectangle(0, 0, thickness, lenght)
        cr.set_line_join(cairo.LINE_JOIN_MITER)
        cr.fill()
        cr.stroke()

    centerY = lenght / 2
    centerX = thickness / 2

    line_w = 2
    half_lw = 1
    arm_len = 4
    body_w = 4

    pt2px_rt = 0
    ratio = dayRange / avgRange

    deltaOL = dayOpen - dayLow
    deltaPL = price - dayLow
    deltaLows =  yLow - dayLow
    deltaOL_y = yOpen - yLow
    deltaPL_y = yClose - yLow

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, thickness, lenght)
    cr = cairo.Context(ims)
    cr.move_to(centerX,centerY)
    cr.scale(1,-1)
    cr.translate(0, -lenght)
    cr.set_line_join(cairo.LINE_CAP_SQUARE)
    # background()

    if ratio < 3:
        ## find max points that fit inside canvas
        maxPts = avgRange * 3
        pt2px_rt = lenght / maxPts
        print(pt2px_rt)

    if ratio >= 3:
        maxPts = dayRange
        pt2px_rt = lenght / maxPts
        print(pt2px_rt)

    def pt2px(pts):
        return pts * pt2px_rt

    def bar(x_start, y_start, len_LH, len_O, len_P, type_func):
        if len_O < len_P:
            cr.set_source_rgb(0.1, 0.8, 0.2)
        else:
            cr.set_source_rgb(0.8, 0, 0.2)
        cr.set_line_width(0)
        # Rectangle(x0, y0, x1, y1)
        #today bar trunk
        cr.rectangle(int(x_start),
                     int(y_start),
                     int(line_w),
                     int(len_LH))
        cr.fill()
        # cr.stroke()

        if type_func == "bar":
            #today arm open
            cr.rectangle(int(x_start + line_w),
                         int(y_start + len_O - half_lw),
                         int(-arm_len),
                         int(line_w))
            #today arm current/close
            cr.rectangle(int(x_start),
                         int(y_start + len_P - half_lw),
                         int(arm_len),
                         int(line_w))

        else:
            #today body
            cr.rectangle(int(x_start - ( (body_w - line_w) / 2) ),
                         int(y_start + len_O),
                         int(body_w),
                         int(len_P - len_O))
        cr.fill()

    def avg_std_box(y_start, avg, std):

        cr.set_source_rgba(0.2, 0.2, 0.2, 0.4)
        cr.set_line_width(0)

        cr.rectangle(0,
                     y_start,
                     thickness,
                     avg)

        cr.fill()
        cr.stroke()

        cr.set_source_rgba(0.3, 0.3, 0.3, 0.2)

        cr.rectangle(0,
                     y_start + avg,
                     thickness,
                     std)


        cr.fill()
        cr.stroke()

    bar_len = pt2px(dayRange)
    bar_low = centerY - (bar_len / 2)
    bar_low_y = bar_low + pt2px(deltaLows)
    bar_len_y = pt2px(yHigh - yLow)

    avg_std_box(bar_low, pt2px(avgRange), pt2px(stdRange))

    bar(centerX + 5,
        bar_low,
        bar_len,
        pt2px(deltaOL),
        pt2px(deltaPL),
        type_)

    bar(centerX - 6,
        bar_low_y,
        bar_len_y,
        pt2px(deltaOL_y),
        pt2px(deltaPL_y),
        type_)

    ims.write_to_png(path)


if __name__ == "__main__":
    drawCandle()
