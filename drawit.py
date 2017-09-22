import cairocffi as cairo

def drawBar(width = 226,
            low52 = 11865.0,
            range52 = 1070.5, #12935.5  52rH
            dopen = 12527.00, #day open
            drange = 57.50,
            path = "gui/bar4.png"):

    left2open_px = (width / range52) * (dopen - low52)
    print(left2open_px)
    range_px = (width / range52) * drange
    print(range_px)

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, 25)
    cr = cairo.Context(ims)

    cr.set_line_width(0)
    cr.set_source_rgb(0, 0, 0)
    cr.rectangle(0, 0, width, 6)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()

    cr.set_source_rgb(255, 255, 255)
    cr.rectangle(left2open_px, 2, range_px, 2)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()

    ims.write_to_png(path)

def drawCandle(height = 200,
            low52 = 11865.0,
            range52 = 1070.5, #12935.5  52rH
            dopen = 12527.00, #day open
            drange = 57.50,
            path = "img/candle.png"):


    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, height)
    cr = cairo.Context(ims)

    cr.set_line_width(0)
    cr.set_source_rgb(0, 0, 0)
    cr.rectangle(0, 0, 10, height)
    cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.fill()
    cr.stroke()


    ims.write_to_png(path)


if __name__ == "__main__":
    drawCandle()
