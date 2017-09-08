# import cairocffi as cairo
# a =0
# a = a+1
#
# print(a)
import cairocffi as cairo




def main():

    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 390, 60)
    cr = cairo.Context(ims)

    cr.set_source_rgb(0, 0, 0)
    cr.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(60)

    cr.move_to(10, 50)
    cr.show_text("INST.T 1000.25")

    ims.write_to_png("img.png")


if __name__ == "__main__":
    main()

def on_draw(self, wid, cr):

    w, h = self.get_size()

    cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(60)

    (x, y, width, height, dx, dy) = cr.text_extents("ZetCode")

    cr.move_to(w/2 - width/2, h/2)
    cr.show_text("ZetCode")
