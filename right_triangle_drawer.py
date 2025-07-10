from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, green, blue
from reportlab.pdfgen import canvas
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

def draw_right_triangle(c, cushion):
    # --- Header & specs ---
    page_w, page_h = letter
    name      = cushion.get('cushion_name', 'Right Triangle Cushion')
    width     = cushion['width']
    length    = cushion['length']
    thickness = cushion.get('thickness', 2)
    zipper    = cushion.get('zipper', 'None')
    # ties      = cushion.get('ties', 'No Ties')
    pipe      = cushion.get('pipe', False)
    qty       = cushion.get('quantity', 1)

    c.setFont("Helvetica-Bold", 14)
    y = page_h - inch
    c.drawString(inch, y, f"{name} (Quantity: {qty})")
    y -= 0.4 * inch

    specs = [
        ("Shape",     "Right Angle Triangle"),
        ("Width",     f"{width} inches"),
        ("Length",    f"{length} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Zipper",    zipper),
        # ("Ties",      ties),
        ("Piping",    "Yes" if pipe else "No"),
        ("Fabric",    cushion.get("fabric", "")),
        ("Fill",      cushion.get("fill", ""))
    ]
    left_x = 1 * inch
    y = page_h - 3 * inch # Adjusted initial y position for specs
    

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        max_value_width = page_w - (left_x + 130 + inch)  # dynamic width limit
        y = draw_wrapped_text(c, left_x + 130, y, value, max_width=max_value_width)
        y -= 4  # extra spacing between spec rows

    # --- Scale & vertex coords ---
    scale = (page_w / 3) / max(width, length)
    w_s = width  * scale
    l_s = length * scale

    x0, y0 = page_w/2 - w_s/2, 1.5 * inch        # bottom-left
    x1, y1 = x0 + w_s,        y0                # bottom-right
    x2, y2 = x0,               y0 + l_s         # top-left

    # --- Draw triangle outline ---
    c.setStrokeColor(black)
    c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    p.lineTo(x2, y2)
    p.close()
    c.drawPath(p)

    # --- Measurement labels ---
    c.setFont("Helvetica", 12)
    c.setFillColor(black)
    # base
    c.drawString(x0 + w_s/2, y0 + 5, f"{width} in")
    # height
    c.drawString(x0 + 5, y0 + l_s/2, f"{length} in")

    # --- Piping ---
    if pipe:
        off = 7
        c.setStrokeColor(blue)
        c.setDash(4,4)
        c.line(x0, y0-off, x1, y1-off)                # bottom
        c.line(x0-off, y0, x2-off, y2)                # left
        # hypotenuse offset by normal
        dx, dy = x2-x1, y2-y1
        h = math.hypot(dx, dy)
        nx, ny = dy/h*off, -dx/h*off
        c.line(x1+nx, y1+ny, x2+nx, y2+ny)
        c.setDash()
        p0 = (x0-off, y0)
        p1 = (x1+nx, y1+ny)
        p2 = (x2-off, y2)
        c.setFont("Helvetica",12)
        c.setFillColor(blue)
        c.drawString(x1+5, y1, f"Piping: {0.5} ''")
    else:
        p0, p1, p2 = (x0,y0), (x1,y1), (x2,y2)

    # --- Thickness label ---
    c.setFont("Helvetica",12)
    c.setFillColor(black)
    c.drawString(x1+25, (y1+y2)/2, f"Thickness: {thickness} ''")

        # ─── Zipper on chosen side ───
    c.setStrokeColor(red)
    c.setLineWidth(1.5)
    c.setFont("Helvetica",12)
    c.setFillColor(red)

    # mid-points of each edge
    mid_base   = ((x0 + x1) / 2, y0)
    mid_height = (x0, (y0 + y2) / 2)
    mid_hyp    = ((x1 + x2) / 2, (y1 + y2) / 2)

    if zipper.lower() == "width":
        # along the base, offset downward
        c.line(x0, y0 - 25, x1, y1 - 25)
        c.drawString(mid_base[0], mid_base[1] - 20, "Zipper")

    elif zipper.lower() == "length":
        # along the left vertical leg, offset left
        c.line(x0 - 15, y0, x2 - 15, y2)
        c.drawString(mid_height[0] - 55, mid_height[1], "Zipper")

    elif zipper.lower() == "hypotenuse":
        # along the slanted side, offset by its normal
        dx, dy = x2 - x1, y2 - y1
        length_h = math.hypot(dx, dy)
        nx, ny = (dy / length_h) * 13, (-dx / length_h) * 13
        c.line(x1 + nx, y1 + ny, x2 + nx, y2 + ny)
        c.drawString(mid_hyp[0] + nx, mid_hyp[1] + ny + 5, "Zipper")

    c.showPage()


if __name__ == "__main__":
    cushion_data = {
        "cushion_name": "Right Triangle Cushion",
        "width": 50,
        "length": 20,
        "thickness": 2,
        "zipper": "width",
        "pipe": True,
        "ties": "2 Side Ties",
        "fabric": "Stamskin F430 - 20290 Chalk Blue / Piezo Blue",
        "fill": "DryFast Foam",
        "quantity": 1
    }
    pdf_filename = "right_triangle_cushion.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    draw_right_triangle(c, cushion_data)
    c.save()
    try:
        from google.colab import files
        files.download(pdf_filename)
    except ImportError:
        print(f"PDF saved as {pdf_filename}")
