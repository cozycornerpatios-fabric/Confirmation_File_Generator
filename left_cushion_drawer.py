from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, blue
import math

def draw_left_cushion(c, cushion):
    # ─── Unpack & Header ───
    page_w, page_h = letter
    name           = cushion.get("cushion_name",   "Left Window Cushions")
    top_thick_in   = cushion["top_width"]           # e.g. small thickness at top
    bot_thick_in   = cushion["bottom_width"]        # large thickness at bottom
    height_in      = cushion["length"]
    thickness_in   = cushion.get("thickness")
    zipper_pos     = cushion.get("zipper")
    piping         = cushion.get("piping",     "No")         # "Yes" or "No"
    qty            = cushion.get("quantity",        1)
    fill           = cushion['fill']
    fabric         = cushion['fabric']

    left_x = inch
    y      = page_h - inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{name} (Qty: {qty})")
    y -= 0.4 * inch

    # ─── Specs table ───
    specs = [
        ("Shape",           "Left Trapezoid"),
        ("Top Thickness",   f"{top_thick_in} in"),
        ("Bottom Thickness",f"{bot_thick_in} in"),
        ("Height",          f"{height_in} in"),
        ("Thickness",       f"{thickness_in} in"),
        ("Zipper",          zipper_pos),
        ("Piping",          piping),
        ("Fill",            fill),
        ("Fabric",          fabric)
    ]
    for label, val in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(left_x + 130, y, val)
        y -= 0.3 * inch

    # ─── Compute scale & corners ───
    margin = 0.75 * inch
    usable_w = page_w*0.5 - 2*margin
    usable_h = y*0.5 - margin
    scale = min(usable_w / max(bot_thick_in, top_thick_in),
                usable_h / height_in)

    top_b = top_thick_in    * scale
    bot_b = bot_thick_in    * scale
    h     = height_in       * scale

    # bottom-left origin
    x0, y0 = (page_w - bot_b)/2, margin
    bl = (x0,       y0)
    br = (x0+bot_b, y0)
    tl = (x0+bot_b-top_b , y0 + h)
    tr = (x0 + bot_b,y0 + h)

    # ─── Piping (blue dashed) ───
    if piping.lower() == "yes":
        c.setStrokeColor(blue)
        c.setDash(4, 4)
        piping_margin = 10
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
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.setFont("Helvetica", 10)
    # bottom thickness
    c.drawString((bl[0]+br[0])/2 - 5, bl[1] + 10, f"{bot_thick_in} in")
    # top thickness
    c.drawString((tl[0]+tr[0])/2 - 5, tl[1] - 10,    f"{top_thick_in} in")
    # height
    c.drawString(tr[0] - 25, (tr[1]+br[1])/2 - 5,      f"{height_in} in")

    # ─── Thickness callout ───
    c.drawString((tl[0] + tr[0] - 10)/2,tr[1] + 15, f"Thickness: {thickness_in} in")
    c.setFillColor(black)

    # ─── Zipper ───
    if(zipper_pos.lower() == "short side"):
        c.setFont("Helvetica", 10)
        c.setFillColor(red)
        c.setStrokeColor(red)
        c.setLineWidth(1.2)
        c.line(tr[0]+20, tr[1], br[0] +20, br[1])
        c.drawString(br[0] +30, (br[1] + tr[1])/2, "Zipper")

    elif(zipper_pos.lower() == "long side"):
        c.setFont("Helvetica", 10)
        c.setFillColor(red)
        c.setStrokeColor(red)
        c.setLineWidth(1.2)
        c.line(bl[0], bl[1]-20, br[0], br[1]-20)
        c.drawString((bl[0]+br[0])/2 - 10, bl[1] - 30, "Zipper")

    c.showPage()

# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     import os
#     c = canvas.Canvas("tapered_bolster.pdf", pagesize=letter)
#     pdf_filename = "tapered_bolster.pdf"
#     data = {
#         "cushion_name": "Tapered Bolster",
#         "top_width":       30,
#         "bottom_width":    50,
#         "thickness":         20,
#         "length":      100,
#         "zipper":        "long side",
#         "piping":        "Yes",
#         "quantity":       1,
#         "fabric":     "Cotton",
#         "fill":       "Silk"
#     }
#     draw_right_cushion(c, data)
#     c.save()
#     try:
#       from google.colab import files
#       files.download(pdf_filename)
#     except ImportError:
#       print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
