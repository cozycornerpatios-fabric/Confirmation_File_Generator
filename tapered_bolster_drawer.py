from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, blue
import math

def draw_wrapped_text(c, x, y, text, max_width, font_name="Helvetica", font_size=12, line_height=14):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split()
    line = ""
    for word in words:
        test_line = f"{line} {word}".strip()
        width = stringWidth(test_line, font_name, font_size)
        if width <= max_width:
            line = test_line
        else:
            c.drawString(x, y, line)
            y -= line_height
            line = word
    if line:
        c.drawString(x, y, line)
        y -= line_height
    return y  # return new y position

def draw_tapered_bolster(c, cushion):
    # ─── Unpack & Header ───
    page_w, page_h = letter
    name           = cushion.get("cushion_name",   "Tapered Bolster")
    top_thick_in   = cushion["top_thickness"]           # e.g. small thickness at top
    bot_thick_in   = cushion["bottom_thickness"]        # large thickness at bottom
    height_in      = cushion["height"]
    thickness_in   = cushion.get("length",       2)
    zipper_pos     = cushion.get("zipper",     "Bottom Length")  # "Top", "Bottom", "Angled"
    piping         = cushion.get("piping",     "No")         # "Yes" or "No"
    qty            = cushion.get("quantity",        1)
    fabric         = cushion.get("fabric")
    fill           = cushion.get("fill")

    left_x = inch
    y      = page_h - inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{name} (Qty: {qty})")
    y -= 0.4 * inch

    # ─── Specs table ───
    specs = [
        ("Shape",           "Right Trapezoid"),
        ("Top Thickness",   f"{top_thick_in} in"),
        ("Bottom Thickness",f"{bot_thick_in} in"),
        ("Height",          f"{height_in} in"),
        ("Thickness",       f"{thickness_in} in"),
        ("Zipper",          zipper_pos),
        ("Piping",          piping),
        ("Fabric",          fabric),
        ("Fill",            fill)
    ]
    left_x = 1 * inch
    # y = page_h - 3 * inch # Adjusted initial y position for specs
    

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        max_value_width = page_w - (left_x + 130 + inch)  # dynamic width limit
        y = draw_wrapped_text(c, left_x + 130, y, value, max_width=max_value_width)
        y -= 4  # extra spacing between spec rows

    # ─── Compute scale & corners ───
    margin = 0.75 * inch
    usable_w = page_w - 2*margin
    usable_h = y - margin
    scale = min(usable_w / max(bot_thick_in, top_thick_in),
                usable_h / height_in)

    top_b = top_thick_in    * scale
    bot_b = bot_thick_in    * scale
    h     = height_in       * scale

    # bottom-left origin
    x0, y0 = (page_w - bot_b)/2, margin
    bl = (x0,       y0)
    br = (x0+bot_b, y0)
    tl = (x0 , y0 + h)
    tr = (x0 + top_b,y0 + h)

    # ─── Piping (blue dashed) ───
    if piping.lower() == "yes":
        c.setStrokeColor(blue)
        c.setDash(4, 4)
        piping_margin = 0.5*scale
        # bottom
        c.line(bl[0], bl[1]-piping_margin , br[0], br[1]-piping_margin)
        # top
        c.line(tl[0], tl[1]+piping_margin, tr[0], tr[1]+ piping_margin)
        # left (vertical)
        c.line(bl[0]-piping_margin, bl[1], tl[0]-piping_margin, tl[1])
        # angled (normal offset)
        dx, dy = tr[0]-br[0], tr[1]-br[1]
        L = math.hypot(dx, dy)
        nx, ny = (dy/L)*5, (-dx/L)*5
        # c.line(br[0]+nx, br[1]+ny, tr[0]+nx, tr[1]+ny)
        # right (vertical)
        c.line(tr[0]+piping_margin, tr[1], br[0]+piping_margin, br[1])
        c.setFont("Helvetica", 10)
        c.setFillColor(blue)
        c.drawString(tr[0]+piping_margin + 5, tr[1], "Piping = 0.5 in")
        c.setDash()

    # ─── Outline ───
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.lines([
        (bl[0], bl[1], br[0], br[1]),
        (br[0], br[1], tr[0], tr[1]),
        (tr[0], tr[1], tl[0], tl[1]),
        (tl[0], tl[1], bl[0], bl[1]),
    ])

    # ─── Dimension labels ───
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    # bottom thickness
    c.drawString((bl[0]+br[0])/2 - 5, bl[1] + 10, f"{bot_thick_in} in")
    # top thickness
    c.drawString((tl[0]+tr[0])/2 - 5, tl[1] - 10,    f"{top_thick_in} in")
    # height
    c.drawString(tl[0] + 8, (bl[1]+tl[1])/2 - 5,      f"{height_in} in")

    # ─── Thickness callout ───
    c.setFont("Helvetica", 10)
    c.drawString(tr[0]+piping_margin + 100,tr[1], f"Thickness: {thickness_in} in")
    c.setFillColor(black)

    # ─── Zipper ───
    c.setFont("Helvetica", 10)
    c.setFillColor(red)
    c.setStrokeColor(red)
    c.setLineWidth(1.2)
    c.line(bl[0], bl[1]-15, br[0], br[1]-15)
    c.drawString((bl[0]+br[0])/2 - 10, bl[1] -25, "Zipper")

    c.showPage()

# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     import os
#     c = canvas.Canvas("tapered_bolster.pdf", pagesize=letter)
#     pdf_filename = "tapered_bolster.pdf"
#     data = {
#         "cushion_name": "Tapered Bolster",
#         "top_thickness":       10,
#         "bottom_thickness":    12,
#         "height":         113,
#         "length":      3,
#         "zipper":        "Angled",
#         "piping":        "Yes",
#         "quantity":       1,
#         "fabric":        "Cotton",
#         "fill":          "Silk"
#     }
#     draw_tapered_bolster(c, data)
#     c.save()
#     try:
#       from google.colab import files
#       files.download(pdf_filename)
#     except ImportError:
#       print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
