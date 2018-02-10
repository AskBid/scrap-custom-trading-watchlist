try:
    import cairo
except Exception as e:
    print(str(e))
try:
    import cairocffi as cairo
except Exception as e:
    print(str(e))
from math import radians
from math import isnan

def drawSVGcandle( lenght = 80, thickness = 23,

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
                ):

    svg ='''    <svg id="svg" style="width: {};height: {};">

    --avg--
    --bar1--
    --bar2--
    </svg>'''.format(thickness,lenght)
    def rect(x,y,w,h,color):
        rect_str = '''<rect x="--x--" y="--y--" width="--w--" height="--h--" id="rectType_--color--"></rect>
    '''
        y = lenght - y -h

        rect_str = rect_str.replace('--x--',str(x))
        rect_str = rect_str.replace('--y--',str(y))
        rect_str = rect_str.replace('--w--',str(w))
        rect_str = rect_str.replace('--h--',str(h))
        rect_str = rect_str.replace('--color--',str(color))
        return rect_str

    def bar(x_start, y_start, len_LH, len_O, len_P, cl):
        body_w = 3
        rects = rect(x_start, y_start, body_w, len_LH, cl)
        arm_w = 1
        if len_O == 0:
            len_O =+ 1
        if len_O == len_LH:
            len_O =- 1
        if len_P == 0:
            len_P =+ 1
        if len_P == len_LH:
            len_P =- 1
        rects = rects + rect(x_start-arm_w, y_start+len_O-1, arm_w, 2, cl)
        rects = rects + rect(x_start+body_w, y_start+len_P-1, arm_w, 2, cl)
        return rects

    pt2px_rt = 0
    ratio = dayRange / avgRange

    if ratio < 2:
        ## find max points that fit inside canvas
        maxPts = avgRange * 3
        pt2px_rt = lenght / maxPts

    if ratio >= 2:
        ## find max points that fit inside canvas
        maxPts = dayRange * 2
        pt2px_rt = lenght / maxPts

    def pt2px(pts):
        return round(pts * pt2px_rt)

    yStart = round(lenght / 4)
    avgRange = pt2px(avgRange)
    color_today_bar = ''
    if dayOpen < price:
        color_today_bar = 'gr'
    else:
        color_today_bar = 'r'
    color_y_bar = ''
    if yOpen < yClose:
        color_y_bar = 'gr'
    else:
        color_y_bar = 'r'
    dayRange = pt2px(dayRange)
    yClose = pt2px(yClose)
    yOpen = pt2px(yOpen)
    yLow = pt2px(yLow)
    yHigh = pt2px(yHigh)
    dayOpen = pt2px(dayOpen)
    price = pt2px(price)
    dayLow = pt2px(dayLow)

    bar1 = bar(14, yStart, dayRange, dayOpen-dayLow, price-dayLow, color_today_bar)
    bar2 = bar(6, yStart-(dayLow-yLow), yHigh-yLow, yOpen-yLow, yClose-yLow, color_y_bar)

    avgs = ''
    for i in range(0,6,2):
        avgs = avgs + rect(0, yStart + (avgRange*i), thickness, avgRange,'g')
    for i in range(2,6,2):
        avgs = avgs + rect(0, yStart + (-avgRange*i), thickness, avgRange,'g')



    svg = svg.replace('--avg--', avgs)
    svg = svg.replace('--bar1--', bar1)
    svg = svg.replace('--bar2--', bar2)


    print(svg)

if __name__ == "__main__":
    drawSVGcandle()
