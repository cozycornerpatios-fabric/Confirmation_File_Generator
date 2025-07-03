from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, green, blue

def draw_l_shape(c, cushion):
    page_width, page_height = letter
    cushion_name = cushion.get('cushion_name', 'L-Shape Cushion')
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
        ("Shape", "L-Shape"),
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

    scale = (page_width / 3) / max(length, top_width, bottom_width, ear)
    x = page_width / 2 - (length * scale) / 2
    y = 1.5 * inch

    main_rect_w = length * scale
    main_rect_h = bottom_width * scale
    ear_w = ear * scale
    ear_h = (bottom_width - top_width) * scale
    main_rect_b = top_width * scale
    piping_margin = 0.1 * inch  # or adjust as needed

    # Anchor setup (choose edge depending on piping presence)
    edge_offset = 0.1 * inch if piping.lower() == "yes" else 0

    anchors = {
        "corner1": (x - edge_offset, y - edge_offset),  # Bottom-left
        "corner2": (x - edge_offset, y + main_rect_h + edge_offset),  # Top-left
        "corner3": (x + main_rect_w + edge_offset, y + main_rect_h + edge_offset),  # Top-right
        "corner4": (x + main_rect_w + edge_offset, y + ear_h - edge_offset),  # Notch corner
        "mid_length": (x + main_rect_w / 2, y - edge_offset),
        "mid_width": (x + main_rect_w + edge_offset, y + main_rect_h / 2),
    }



    c.setStrokeColor(black)
    c.setLineWidth(1)

    p = c.beginPath()
    p.moveTo(x, y)
    p.lineTo(x, y + main_rect_h)
    p.lineTo(x + main_rect_w, y + main_rect_h)
    p.lineTo(x + main_rect_w, y + ear_h)
    p.lineTo(x + main_rect_w - ear_w, y + ear_h)
    p.lineTo(x + main_rect_w - ear_w, y)
    p.close()
    c.drawPath(p)

    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(x + main_rect_w / 2, y + main_rect_h - 10, f"{length}\"")
    c.drawCentredString(x + 10, y + main_rect_h / 2, f"{bottom_width}\"")
    c.drawCentredString(x + main_rect_w - 20, y + ear_h + main_rect_b / 2, f"{top_width}\"")
    c.drawCentredString(x + main_rect_w - ear_w/2, y + ear_h + 5, f"{ear}\"")

    if piping.lower() in ["yes", "piping"]:
        c.setStrokeColor(blue)
        c.setLineWidth(1)
        p2 = c.beginPath()
        p2.moveTo(x - piping_margin, y - piping_margin)
        p2.lineTo(x - piping_margin, y + main_rect_h + piping_margin)
        p2.lineTo(x + main_rect_w + piping_margin, y + main_rect_h + piping_margin)
        p2.lineTo(x + main_rect_w + piping_margin, y + ear_h - piping_margin)
        p2.lineTo(x + main_rect_w - ear_w - piping_margin, y + ear_h - piping_margin)
        p2.lineTo(x + main_rect_w - ear_w - piping_margin, y - piping_margin)
        p2.close()
        c.drawPath(p2)
        # Label and pointer line for Piping
        x1,y1 = anchors["corner4"]
        label_x = x1 - main_rect_w/2
        label_y = y1 - 5 - piping_margin

        # Label text
        c.setFont("Helvetica", 10)
        c.setFillColor(blue)
        c.drawCentredString(label_x, label_y, "Piping")

        # # Connector line
        # c.setStrokeColor(blue)
        # c.setLineWidth(1)
        # c.line(label_x, label_y + 2, label_x, y1 - piping_margin)


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
        elif direction == "left":
            c.line(x, y, x - offset, y + offset)
            c.line(x, y, x - offset, y - offset)
            c.drawCentredString(x - offset - 5, y, "Tie")
        elif direction == "right":
            c.line(x, y, x + offset, y + offset)
            c.line(x, y, x + offset, y - offset)
            c.drawCentredString(x + offset + 5, y, "Tie")

    if ties == "2 Corner Ties along length":
        draw_tie(*anchors["corner2"], "up")
        draw_tie(*anchors["corner3"], "up")

    elif ties == "2 Length side ties":
        x1,y1 = anchors["corner2"]
        x2,y2 = anchors["corner3"]
        x1 += main_rect_w*0.25
        x2 = x2 - main_rect_w*0.25
        draw_tie(x1,y1,"up")
        draw_tie(x2,y2,"up")

    elif ties == "2 ties along the width":
        x1,y1 = anchors["corner3"]
        x2,y2 = anchors["corner4"]
        y1 = y1 - main_rect_h*0.25
        y2 += main_rect_h*0.25
        draw_tie(x1,y1,"right")
        draw_tie(x2,y2,"right")

    elif ties == "3 Corner ties":
        draw_tie(*anchors["corner4"], "down")
        draw_tie(*anchors["corner2"], "left")
        draw_tie(*anchors["corner3"], "up")


    



    if zipper_position:
      c.setStrokeColor(red)
      c.setLineWidth(2)
      c.setFillColor(red)
      c.setFont("Helvetica-Bold", 10)

      if zipper_position == "Length":
          # Along the long horizontal edge (top of L)
          x1 = x
          x2 = x + main_rect_w
          y_z = y + main_rect_h + 0.1 * inch
          c.line(x1, y_z + 10, x2, y_z + 10)
          c.drawString((x1 + x2) / 2 - 20, y_z + 15, "Zipper")

      elif zipper_position == "Top Width":
          # Inside vertical on right side (L notch)
          x1 = x + main_rect_w
          y1 = y + ear_h
          y2 = y + main_rect_h
          c.line(x1 + 0.2 * inch, y1, x1 + 0.2 * inch, y2)
          c.drawString(x1 + 0.3 * inch, (y1 + y2) / 2, "Zipper")

      elif zipper_position == "Bottom Width":
          # Bottom horizontal segment (bottom leg of L)
          x1 = x + main_rect_w - ear_w
          x2 = x + main_rect_w
          y_z = y + ear_h
          c.line(x1, y_z - 0.2 * inch, x2, y_z - 0.2 * inch)
          c.drawString((x1 + x2) / 2 - 20, y_z - 0.5 * inch, "Zipper")


    c.showPage()
