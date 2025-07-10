from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black,blue,green,red
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

def draw_curved(c, cushion):
    page_width, page_height = letter

    # --- pull in your specs ---
    cushion_name      = cushion.get('cushion_name', 'Curved Cushion Specs')
    width_in          = cushion['width']
    side_length_in    = cushion['side_length']
    middle_length_in  = cushion['middle_length']
    thickness         = cushion.get('thickness', 1)
    quantity          = cushion.get('quantity', 1)
    piping            = cushion.get('piping')
    zipper_on         = cushion.get('zipper')
    ties              = cushion.get('ties')
    fabric            = cushion.get('fabric')
    fill              = cushion.get('fill')

    # --- header and spec table ---
    left_x = inch
    y = page_height - inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Qty: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape",        "Curved"),
        ("Width",        f"{width_in}\""),
        ("Side Length",  f"{side_length_in}\""),
        ("Middle Length",f"{middle_length_in}\""),
        ("Thickness",    f"{thickness}\""),
        ("Fabric",       fabric),
        ("Fill",         fill)
    ]
    left_x = 1 * inch
    # y = page_height - 3 * inch # Adjusted initial y position for specs
    

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        max_value_width = page_width - (left_x + 130 + inch)  # dynamic width limit
        y = draw_wrapped_text(c, left_x + 130, y, value, max_width=max_value_width)
        y -= 4  # extra spacing between spec rows

    # --- compute scale so it fits on the page ---
    diagram_w = page_width  / 2.0
    diagram_h = page_height / 3.0
    scale    = min(diagram_w / width_in, diagram_h / middle_length_in)

    w         = width_in        * scale
    rect_h    = side_length_in  * scale
    head_b    = (middle_length_in - side_length_in) * scale  # ellipse “radius” above rect

    # origin of the bottom-left of the rect
    x0 = (page_width - w) / 2
    y0 = inch

    # --- draw outline: flat bottom + straight sides + curved top ---
    c.setStrokeColor(black)
    c.setLineWidth(1)
    # bottom edge
    c.line(x0, y0, x0 + w, y0)
    # left and right sides
    c.line(x0, y0, x0, y0 + rect_h)
    c.line(x0 + w, y0, x0 + w, y0 + rect_h)
    # top curve = half-ellipse
    c.arc(x0,
          y0 + rect_h - head_b,
          x0 + w,
          y0 + rect_h + head_b,
          startAng=0,
          extent=180)

        # --- PIPING OUTLINE (0.5" margin) ---
    if piping.lower() in ["yes", "piping"]:
        # 0.5" of physical piping around the cushion
        piping_margin = 0.5 *scale

        c.setStrokeColor(blue)    # or whatever color you like
        c.setLineWidth(1)

        # bottom edge
        c.line(x0 - piping_margin, y0 - piping_margin,
               x0 + w + piping_margin, y0 - piping_margin)
        # left side
        c.line(x0 - piping_margin, y0 - piping_margin,
               x0 - piping_margin, y0 + rect_h + piping_margin)
        # right side
        c.line(x0 + w + piping_margin, y0 - piping_margin,
               x0 + w + piping_margin, y0 + rect_h + piping_margin)

        # label for piping
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(blue)
        c.drawCentredString(x0 + w + piping_margin + 30, y0 + rect_h/2, f"Piping")

        # curved top (half‐ellipse) expanded by piping_margin
        c.arc(x0 - piping_margin,
              y0 + rect_h - head_b - piping_margin,
              x0 + w + piping_margin,
              y0 + rect_h + head_b + piping_margin,
              startAng=0, extent=180)



    def draw_tie(c, x, y, direction, orientation='horizontal'):
        """
        c           : your Canvas
        x, y        : attachment point in page-points
        direction   : 'left' / 'right' / 'up' / 'down'
        orientation : 'horizontal' draws ↔ style, 'vertical' draws ↕ style
        """
        # how long each arm of the tie is, in page-points
        tie_len = 0.3 * inch
        c.setDash()

        if orientation == 'horizontal':
            if direction == 'left':
                c.line(x, y, x - tie_len, y - tie_len)
                c.line(x, y, x - tie_len, y + tie_len)
            elif direction == 'right':
                c.line(x, y, x + tie_len, y - tie_len)
                c.line(x, y, x + tie_len, y + tie_len)

        elif orientation == 'vertical':
            if direction == 'down':
                c.line(x, y, x - tie_len, y - tie_len)
                c.line(x, y, x + tie_len, y - tie_len)
            elif direction == 'up':
                c.line(x, y, x - tie_len, y + tie_len)
                c.line(x, y, x + tie_len, y + tie_len)

        # small “Tie” label
        c.setFont("Helvetica", 8)
        c.setFillColor(green)
        if direction in ('left','right'):
            label_x = x + ( -15 if direction=='left' else + 15 )
            label_y = y
        else:
            label_x = x
            label_y = y + ( -20 if direction=='down' else +2 * tie_len + 2 )

        c.drawCentredString(label_x, label_y, "Tie")


        # --- TIES (attach to outline: piping if on, else shape edge) ---
        # --- TIES (attach to piping outline if on, else cushion edge) ---
    # real‐world inch offset → page points
    tie_offset_in = cushion.get('tie_offset_from_corner', 0)
    tie_off       = tie_offset_in * scale

    # how far the outline (piping) sits outside the raw shape?
    outline_margin = 0.5 * scale if piping.lower() in ["yes","piping"] else 0

    # recompute the “outline” origin + total dims
    xo      = x0 - outline_margin
    yo      = y0 - outline_margin
    total_w = w  + 2*outline_margin
    total_h = rect_h + 2*outline_margin

    c.setStrokeColor(green)
    c.setLineWidth(1.2)
    c.setDash(1, 2)

    opt = ties.lower()

    if opt in ["no ties", "none"]:
        pass

    elif opt in ["2 front corner ties", "2 front corner"]:
        # bottom‐left
        draw_tie(c, xo + tie_off,         yo,                     'down',  'vertical')
        # bottom‐right
        draw_tie(c, xo + total_w - tie_off, yo,                   'down',  'vertical')

    elif opt in ["2 curved edge ties", "2 curved edge"]:

    # ellipse center and radii (works whether or not piping is on)
        cx = xo + total_w/2
        cy = yo + total_h - outline_margin    # always the top of the raw cushion
        rx = total_w  / 2
        ry = head_b    + outline_margin       # half-ellipse height plus any piping margin

        # pick an angle (45° here) to slide the ties inward along the arc
        theta = math.radians(45)

        # compute left‐tie coords
        x_l = cx - rx * math.cos(theta)
        y_l = cy + ry * math.sin(theta)
        draw_tie(c, x_l, y_l, 'left',  'horizontal')

        # compute right‐tie coords
        x_r = cx + rx * math.cos(theta)
        y_r = y_l
        draw_tie(c, x_r, y_r, 'right', 'horizontal')


    elif opt in ["4 corner ties", "4 corner", "4 corners"]:
        # bottom‐left
        draw_tie(c, xo + tie_off,         yo,                     'down',  'vertical')
        # bottom‐right
        draw_tie(c, xo + total_w - tie_off, yo,                   'down',  'vertical')
        # ellipse center and radii (works whether or not piping is on)
        cx = xo + total_w/2
        cy = yo + total_h - outline_margin    # always the top of the raw cushion
        rx = total_w  / 2
        ry = head_b    + outline_margin       # half-ellipse height plus any piping margin

        # pick an angle (45° here) to slide the ties inward along the arc
        theta = math.radians(45)

        # compute left‐tie coords
        x_l = cx - rx * math.cos(theta)
        y_l = cy + ry * math.sin(theta)
        draw_tie(c, x_l, y_l, 'left',  'horizontal')

        # compute right‐tie coords
        x_r = cx + rx * math.cos(theta)
        y_r = y_l
        draw_tie(c, x_r, y_r, 'right', 'horizontal')


    else:
        # unexpected option
        print(f"Warning: unrecognized ties option: {ties!r}")




    # --- dimension labels ---
    c.setFillColor(black)
    c.setStrokeColor(black)
    c.setFont("Helvetica", 10)
    # Width (beneath bottom)
    c.drawCentredString(x0 + w/2, y0 + 12, f"{width_in}\"")
    # Side length (along left side)
    c.drawCentredString(x0 + 12, y0 + rect_h/2, f"{side_length_in}\"")
    # thickness
    c.drawCentredString(x0 - 50, y0 + rect_h/2, f"Thickness = {thickness}\"")
    # Middle length (arrow up the center)
    mid_x = x0 + w/2
    c.setDash(1, 2)
    c.line(mid_x, y0, mid_x, y0 + rect_h + head_b)
    c.setDash()
    c.drawString(mid_x + 5, y0 + (rect_h + head_b)/2, f"{middle_length_in}\"")


        # --- ZIPPER (red) ---
    if zipper_on.lower() in ["front side", "front"]:
        # flat/front edge zipper
        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.line(x0, y0 - 20, x0 + w, y0 - 20)
        # optional label
        c.setFillColor(red)
        c.setFont("Helvetica", 12)
        c.drawString(x0 + w/2 - 10, y0 - 32, "Zipper")

    elif zipper_on.lower() in ["curved side", "curved"]:
        # curved/top arc zipper
        c.setStrokeColor(red)
        c.setLineWidth(2)
        # re-draw just the top half-ellipse in red
        c.arc(
            x0 - 20,
            y0 + rect_h - head_b + 20,
            x0 + w + 20,
            y0 + rect_h + head_b + 20,
            startAng=0,
            extent=180
        )
        # optional label near center of arc
        mid_x = x0 + w/2
        label_y = y0 + rect_h + head_b + 24
        c.setFillColor(red)
        c.setFont("Helvetica", 12)
        c.drawString(mid_x - 15, label_y, "Zipper")


    c.showPage()


# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from math import pi, cos, sin
#     import os

#     test_cushion = {
#         "cushion_name": "Test Cushion - 2 Same Side Long",
#         # "length": 73,
#         "width": 18,
#         # "height": 3,
#         # "top_width": 17.5,
#         # "bottom_width": 37,
#         # "ear": 17.5,
#         "fill": "Poly Fiber",
#         "fabric": "Outdoor Canvas",
#         "side_length": 10,
#         "middle_length": 30,
#         "zipper": "front", # front side/ curved side
#         "piping": "yes",
#         "ties": "4 corner ties",  # 2 front corner ties/ 2 curved edge ties/ 4 corner ties
#         "quantity": 1,
#         "diameter" : 100,
#         "thickness" : 10
#     }

#     pdf_filename = "test_output.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     draw_curved(c, test_cushion)
#     c.save()

#     # Force download link for Colab
#     try:
#         from google.colab import files
#         files.download(pdf_filename)
#     except ImportError:
#         print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
