from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, green, blue

def draw_t_shape(c, cushion):
    page_width, page_height = letter
    cushion_name = cushion.get('cushion_name', 'T-Shape Cushion')
    length = cushion['length']
    top_width = cushion['top_width']
    bottom_width = cushion['bottom_width']
    ear = cushion['ear']
    height = cushion['height']
    fill = cushion['fill']
    fabric = cushion['fabric']
    zipper_position = cushion['zipper']
    piping = cushion.get('piping', 'No')
    ties = cushion.get('ties', 'None')
    quantity = cushion.get('quantity', 1)

    c.setFont("Helvetica-Bold", 14)
    y = page_height - inch
    c.drawString(inch, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape", "T-Shape"),
        ("Length", f"{length} inches"),
        ("Top Width", f"{top_width} inches"),
        ("Bottom Width", f"{bottom_width} inches"),
        ("Ear", f"{ear} inches"),
        ("Height", f"{height} inches"),
        ("Fill", fill),
        ("Fabric", fabric),
        ("Zipper Position", zipper_position),
        ("Piping", piping),
        ("Ties", ties)
    ]

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(inch + 120, y, value)
        y -= 0.3 * inch

    # Diagram calculation
    scale = (page_width / 3) / max(length, top_width, bottom_width, ear)
    x = page_width / 2 - (length * scale) / 2
    y = 1.5 * inch

    body_w = length * scale
    body_h = top_width * scale
    notch_w = ear * scale
    notch_h = (top_width - bottom_width) * scale
    base_h = bottom_width * scale

    # Anchor points
    anchors = {
        "corner1": (x, y),  # Bottom-left
        "corner2": (x, y + base_h),  # Top-left
        "corner3": (x + notch_w, y + base_h),  # Top-right
        "corner4": (x + notch_w, y + base_h - notch_h/2),  # Notch inner
        "corner5": (x + body_w, y + base_h - notch_h/2),  # Notch far
        "corner6": (x + body_w, y + notch_h/2),  # Bottom-right
        "corner7": (x + notch_w, y + notch_h/2),  # Bottom-right
        "corner8": (x + notch_w, y)  # Bottom-right
    }

    # Draw shape
    c.setStrokeColor(black)
    c.setLineWidth(1)
    p = c.beginPath()
    p.moveTo(*anchors["corner1"])
    p.lineTo(*anchors["corner2"])
    p.lineTo(*anchors["corner3"])
    p.lineTo(*anchors["corner4"])
    p.lineTo(*anchors["corner5"])
    p.lineTo(*anchors["corner6"])
    p.lineTo(*anchors["corner7"])
    p.lineTo(*anchors["corner8"])
    p.close()
    c.drawPath(p)

    # Dimension labels
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(x + body_w / 2, y + base_h + 10, f"{length}\"")
    c.drawCentredString(x + 15, y + base_h / 2, f"{bottom_width}\"")
    c.drawCentredString(x + body_w - 20, y + notch_h + 10, f"{top_width}\"")
    c.drawCentredString(x + body_w - notch_w / 2, y + notch_h + 5, f"{ear}\"")

    # Piping
    if piping.lower() == "yes":
        margin = 0.1 * inch
        c.setStrokeColor(blue)
        p2 = c.beginPath()
        p2.moveTo(x - margin, y - margin)
        p2.lineTo(x - margin, y + base_h + margin)
        p2.lineTo(x + body_w + margin, y + base_h + margin)
        p2.lineTo(x + body_w + margin, y + notch_h - margin)
        p2.lineTo(x + body_w - notch_w - margin, y + notch_h - margin)
        p2.lineTo(x + body_w - notch_w - margin, y - margin)
        p2.close()
        c.drawPath(p2)

        c.setFont("Helvetica", 9)
        c.setFillColor(blue)
        c.drawString(x + body_w / 2 - 10, y + base_h + 20, "Piping")

    # Ties (basic support)
    def draw_tie(x, y, direction):
        offset = 20
        c.setStrokeColor(green)
        c.setFillColor(green)
        c.setLineWidth(1.2)
        if direction == "up":
            c.line(x, y, x - offset, y + offset)
            c.line(x, y, x + offset, y + offset)
            c.drawCentredString(x, y + offset + 5, "Tie")
        elif direction == "down":
            c.line(x, y, x - offset, y - offset)
            c.line(x, y, x + offset, y - offset)
            c.drawCentredString(x, y - offset - 5, "Tie")

    if ties == "2 Corner Ties along length":
        draw_tie(*anchors["corner2"], "up")
        draw_tie(*anchors["corner3"], "up")

    elif ties == "2 ties along the width":
        draw_tie(*anchors["corner3"], "down")
        draw_tie(*anchors["corner4"], "down")

    elif ties == "3 Corner ties":
        draw_tie(*anchors["corner2"], "up")
        draw_tie(*anchors["corner3"], "up")
        draw_tie(*anchors["corner6"], "down")

    # Zipper
    if zipper_position:
        c.setStrokeColor(red)
        c.setFillColor(red)
        c.setLineWidth(2)
        if zipper_position == "Length":
            c.line(x, y + base_h + 10, x + body_w, y + base_h + 10)
            c.drawString(x + body_w / 2 - 20, y + base_h + 15, "Zipper")
        elif zipper_position == "Top Width":
            c.line(x + body_w + 10, y + notch_h, x + body_w + 10, y + base_h)
            c.drawString(x + body_w + 15, y + base_h - 10, "Zipper")
        elif zipper_position == "Bottom Width":
            c.line(x + body_w - notch_w, y - 10, x + body_w, y - 10)
            c.drawString(x + body_w - notch_w / 2 - 20, y - 20, "Zipper")

    c.showPage()
