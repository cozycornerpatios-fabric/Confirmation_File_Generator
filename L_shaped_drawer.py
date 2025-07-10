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
    thickness = cushion['thickness']
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
        ("Thickness", f"{thickness} inches"),
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


    anchors = {
        "corner1": (x , y ),  # Bottom-left
        "corner2": (x , y + main_rect_h ),  # Top-left
        "corner3": (x + main_rect_w , y + main_rect_h ),  # Top-right
        "corner4": (x + main_rect_w , y + ear_h),  # Notch corner
        "corner5": (x + ear_w, y + ear_h),
        "corner6": (x + ear_w , y ),
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
    p.close()
    c.drawPath(p)

    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(x + main_rect_w / 2, y + main_rect_h - 10, f"{length}\"")
    c.drawCentredString(x + 10, y + main_rect_h / 2, f"{bottom_width}\"")
    c.drawCentredString(x + main_rect_w - 20, y + ear_h + main_rect_b / 2, f"{top_width}\"")
    c.drawCentredString((anchors["corner1"][0] + anchors["corner6"][0])/2,y+10, f"{ear}\"")

    if piping.lower() == "yes":
        c.setStrokeColor(blue)
        c.setLineWidth(2)
        c.setDash(3, 3)

        # Start piping path with margin
        p2 = c.beginPath()
        # Move to bottom-left with margin
        p2.moveTo(anchors["corner1"][0] - piping_margin, anchors["corner1"][1] - piping_margin)
        # Left side up
        p2.lineTo(anchors["corner2"][0] - piping_margin, anchors["corner2"][1] + piping_margin)
        # Top left ear
        p2.lineTo(anchors["corner3"][0] + piping_margin, anchors["corner3"][1] + piping_margin)
        # Inward notch
        p2.lineTo(anchors["corner4"][0] + piping_margin, anchors["corner4"][1] - piping_margin)
        # Across notch top
        p2.lineTo(anchors["corner5"][0] + piping_margin, anchors["corner5"][1] - piping_margin)
        # Right side down notch
        p2.lineTo(anchors["corner6"][0] + piping_margin, anchors["corner6"][1] - piping_margin)
        # Close back to start
        p2.close()

        c.drawPath(p2)
        c.setDash()  # Reset
        # Label and pointer line for Piping
        x1,y1 = anchors["corner4"]
        label_x = x1 + piping_margin + 5
        label_y = y1 - 10 - piping_margin

        # Label text
        c.setFont("Helvetica", 10)
        c.setFillColor(blue)
        c.drawCentredString(label_x, label_y, "Piping")

        # # Connector line
        # c.setStrokeColor(blue)
        # c.setLineWidth(1)
        # c.line(label_x, label_y + 2, label_x, y1 - piping_margin)

    #thickness label
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(x + main_rect_w + 40, y + main_rect_h/2 - 20, f"Thickness: {thickness}\"")
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


    tie_anchors = {}
    if piping.lower() == "yes":
      # Calculate tie anchor points with piping margin
      tie_anchors = {
        "corner1": (anchors["corner1"][0] - piping_margin, anchors["corner1"][1] - piping_margin),
        "corner2": (anchors["corner2"][0] - piping_margin, anchors["corner2"][1] + piping_margin),
        "corner3": (anchors["corner3"][0] + piping_margin, anchors["corner3"][1] + piping_margin),
        "corner4": (anchors["corner4"][0] + piping_margin, anchors["corner4"][1] - piping_margin),
        "corner5": (anchors["corner5"][0] + piping_margin, anchors["corner5"][1] - piping_margin),
        "corner6": (anchors["corner6"][0] + piping_margin, anchors["corner6"][1] - piping_margin)
      }
    else:
      # Use main shape anchors if no piping
      tie_anchors = anchors

    if ties == "2 Corner Ties along length":
        draw_tie(*tie_anchors["corner2"], "up")
        draw_tie(*tie_anchors["corner3"], "up")

    elif ties == "2 Length side ties":
        x1,y1 = tie_anchors["corner2"]
        x2,y2 = tie_anchors["corner3"]
        x1 += main_rect_w*0.25
        x2 = x2 - main_rect_w*0.25
        draw_tie(x1,y1,"up")
        draw_tie(x2,y2,"up")

    elif ties == "2 ties along the width":
        x1,y1 = tie_anchors["corner1"]
        x2,y2 = tie_anchors["corner2"]
        y1 += main_rect_h*0.25
        y2 = y2 - main_rect_h*0.25
        draw_tie(x1,y1,"left")
        draw_tie(x2,y2,"left")

    elif ties == "3 Corner ties":
        draw_tie(*tie_anchors["corner1"], "left")
        draw_tie(*tie_anchors["corner2"], "up")
        draw_tie(*tie_anchors["corner3"], "right")






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
          x_z = anchors["corner1"][0] - 5 - piping_margin
          y1 = anchors["corner1"][1] - piping_margin
          y2 = anchors["corner2"][1] + piping_margin
          y_z = (y1 + y2)/2
          c.line(x_z, y1, x_z, y2)
          c.drawString(x_z - 40, y_z, "Zipper")


    c.showPage()


# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     import os

#     test_cushion = {
#         "cushion_name": "Test Cushion - 2 Same Side Long",
#         "length": 73,
#         # "width": 18,
#         "thickness": 3,
#         "top_width": 17.5,
#         "bottom_width": 37,
#         "ear": 5,
#         "fill": "Poly Fiber",
#         "fabric": "Outdoor Canvas",
#         "zipper": "Top Width",
#         "piping": "yes",
#         "ties": "Top Width",  # Try with "2 Same Side Short"
#         "quantity": 1
#     }

#     pdf_filename = "test_output.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     draw_l_shape(c, test_cushion)
#     c.save()

#     # Force download link for Colab
#     try:
#         from google.colab import files
#         files.download(pdf_filename)
#     except ImportError:
#         print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
