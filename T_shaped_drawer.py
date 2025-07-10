from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, green, blue
from reportlab.pdfgen import canvas

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


def draw_t_shape(c, cushion):
    page_width, page_height = letter
    cushion_name = cushion.get('cushion_name', 'T-Shape Cushion')
    length = cushion['length']
    top_width = cushion['top_width']
    bottom_width = cushion['bottom_width']
    ear = cushion['ear']
    thickness = cushion['thickness']
    fill = cushion['fill']
    fabric = cushion['fabric']
    zipper_position = cushion['zipper']
    piping = cushion.get('piping', 'No')
    ties = cushion.get('ties','No ties')
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
        ("Thickness", f"{thickness} inches"),
        ("Fill", fill),
        ("Fabric", fabric),
        ("Zipper Position", zipper_position),
        ("Piping", piping),
        ("Ties", ties)
    ]

    left_x = 1 * inch
    y = page_height - 3 * inch # Adjusted initial y position for specs
    

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        max_value_width = page_width - (left_x + 130 + inch)  # dynamic width limit
        y = draw_wrapped_text(c, left_x + 130, y, value, max_width=max_value_width)
        y -= 4  # extra spacing between spec rows

    # Diagram calculation
    scale = (page_width / 3) / max(length, top_width, bottom_width, ear)
    x = page_width / 2 - (length * scale) / 2
    y = 1.5 * inch

    body_w = length * scale
    body_h = top_width * scale
    notch_w = ear * scale
    notch_h = (top_width - bottom_width) * scale
    base_h = bottom_width * scale
    rem_e = body_w - notch_w

    # Anchor points for the main shape
    anchors = {
        "corner1": (x, y),  # Bottom-left
        "corner2": (x, y + body_h),  # Top-left
        "corner3": (x + notch_w, y + body_h),  # Top-right
        "corner4": (x + notch_w, y + body_h - notch_h/2),  # Notch inner
        "corner5": (x + body_w, y + body_h - notch_h/2),  # Notch far
        "corner6": (x + body_w, y + notch_h/2),  # Notch far
        "corner7": (x + notch_w, y + notch_h/2),  # Notch inner
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
    c.drawCentredString(x + body_w / 2,  y - 20, f"{length}\"")
    # Draw length dimension dotted line
    c.setDash(3, 3)  # Set dash pattern: 3 points on, 3 points off
    c.line(x, y - 10, x + body_w, y - 10)
    c.setDash()  # Reset dash to solid
    c.drawCentredString(x + 15, y + base_h / 2, f"{top_width}\"")
    c.drawCentredString(x + body_w - 20, y + notch_h + base_h/2, f"{bottom_width}\"")
    c.drawCentredString(x + notch_w/2 , y + 10, f"{ear}\"")

    # Thickness label
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawString(x + body_w + 40, y + body_h/2 - 20, f"Thickness: {thickness}\"")


    # Piping
    piping_margin = 0.05 * inch
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
        p2.lineTo(anchors["corner4"][0] + piping_margin, anchors["corner4"][1] + piping_margin)
        # Across notch top
        p2.lineTo(anchors["corner5"][0] + piping_margin, anchors["corner5"][1] + piping_margin)
        # Right side down notch
        p2.lineTo(anchors["corner6"][0] + piping_margin, anchors["corner6"][1] - piping_margin)
        # Inward notch bottom
        p2.lineTo(anchors["corner7"][0] + piping_margin, anchors["corner7"][1] - piping_margin)
        # Bottom right
        p2.lineTo(anchors["corner8"][0] + piping_margin, anchors["corner8"][1] - piping_margin)
        # Close back to start
        p2.close()

        c.drawPath(p2)
        c.setDash()  # Reset

        # Piping label and leader line on the right side
        c.setFont("Helvetica", 9)
        c.setFillColor(blue)
        label_text = "Piping"
        label_x = x + body_w + 20  # Position the label to the right of the shape
        label_y = y + body_h/2  # Vertically center the label on the right side
        c.drawString(label_x, label_y, label_text)

        # Draw leader line from label to piping outline on the right edge
        line_start_x = label_x
        line_start_y = label_y + c.stringWidth(label_text, "Helvetica", 9) / 2 # Start from the right edge of the label
        line_end_x = anchors["corner5"][0] + piping_margin # Connect to the right edge of the piping outline
        line_end_y = y + body_h/2 # Vertically align with the label
        c.setStrokeColor(blue)
        c.setLineWidth(0.5)
        c.line(line_start_x, line_start_y, line_end_x, line_end_y)


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
        elif direction == "left":
            c.line(x, y, x - offset, y + offset)
            c.line(x, y, x - offset, y - offset)
            c.drawCentredString(x - offset - 5, y, "Tie")
        elif direction == "right":
            c.line(x, y, x + offset, y + offset)
            c.line(x, y, x + offset, y - offset)
            c.drawCentredString(x + offset + 5, y, "Tie")


    # Draw ties based on type
    # Determine tie anchor points based on piping
    tie_anchors = {}
    if piping.lower() == "yes":
      # Calculate tie anchor points with piping margin
      tie_anchors = {
        "corner1": (x - piping_margin, y - piping_margin),
        "corner2": (x - piping_margin, y + body_h + piping_margin),
        "corner3": (x + notch_w + piping_margin, y + body_h + piping_margin),
        "corner4": (x + notch_w + piping_margin, y + body_h - notch_h/2 + piping_margin),
        "corner5": (x + body_w + piping_margin, y + body_h - notch_h/2 + piping_margin),
        "corner6": (x + body_w + piping_margin, y + notch_h/2 - piping_margin),
        "corner7": (x + notch_w + piping_margin, y + notch_h/2 - piping_margin),
        "corner8": (x + notch_w + piping_margin, y - piping_margin)
      }
    else:
      # Use main shape anchors if no piping
      tie_anchors = anchors


    if ties == "No ties":
        pass  # nothing to draw

    elif ties == "2 Corner ties top width":
        draw_tie(*tie_anchors["corner1"], "left")
        draw_tie(*tie_anchors["corner2"], "left")

    elif ties == "2 Corner ties bottom width":
        draw_tie(*tie_anchors["corner5"], "up")
        draw_tie(*tie_anchors["corner6"], "down")

    elif ties == "2 Side ties-along length":
        # Need to calculate midpoints for ties along length, adjusting for piping
        if piping.lower() == "yes":
            mid_x_left = tie_anchors["corner1"][0] + 0.25*(body_w - notch_w)
            mid_x_right = tie_anchors["corner8"][0] - 0.25*(body_w - notch_w)
            draw_tie(mid_x_left, tie_anchors["corner1"][1], "down")
            draw_tie(mid_x_right, tie_anchors["corner8"][1], "down")
        else:
            mid_x_left = anchors["corner1"][0] + 0.25*(body_w - notch_w)
            mid_x_right = anchors["corner8"][0] - 0.25*(body_w - notch_w)
            draw_tie(mid_x_left,anchors["corner1"][1], "down")
            draw_tie(mid_x_right,anchors["corner8"][1], "down")


    elif ties == "2 Corner ties":
        draw_tie(*tie_anchors["corner3"], "up")
        draw_tie(*tie_anchors["corner8"], "down")

    elif ties == "4 Corner ties":
        draw_tie(*tie_anchors["corner1"], "down")
        draw_tie(*tie_anchors["corner6"], "down")
        draw_tie(*tie_anchors["corner2"], "up")
        draw_tie(*tie_anchors["corner5"], "up")

    # Zipper
    # Zipper (positioned according to reference diagrams)
    if zipper_position:
        c.setStrokeColor(red)
        c.setFillColor(red)
        c.setLineWidth(1.5)
        c.setFont("Helvetica", 8)

        inset = 5  # small gap inside edges

    if zipper_position == "Top Width":
        # Top edge of main body
        x1 = anchors["corner1"][0] - inset
        y1 = anchors["corner1"][1]
        x2 = anchors["corner2"][0] - inset
        y2 = anchors["corner2"][1]
        c.line(x1- inset, y1, x2-inset, y2)
        c.drawString((x1 + x2)/2 - 30 , y1 + 30, "Zipper")

    elif zipper_position == "Bottom Width":
        # Bottom edge of main body

        x1 = anchors["corner5"][0] + inset
        y1 = anchors["corner5"][1]
        x2 = anchors["corner6"][0] + inset
        y2 = anchors["corner6"][1]
        c.line(x1+inset, y1, x2+inset, y2)
        c.drawString((x1 + x2)/2 + 10, y1 - 30, "Zipper")

    elif zipper_position == "Ear":
        # Inside ear notch
        x1 = anchors["corner1"][0]
        y1 = anchors["corner1"][1] - inset
        x2 = anchors["corner8"][0]
        y2 = anchors["corner8"][1] - inset
        c.line(x1, y1-inset, x2, y2-inset)
        c.drawString((x1 + x2)/2 - 10, y1 - 8, "Zipper")

    elif zipper_position == "Length":
        label_gap = 5

        # Vertical zipper along left length edge
        x1 = anchors["corner2"][0]
        y1 = anchors["corner2"][1] + inset
        x2 = anchors["corner5"][0]
        y2 = anchors["corner2"][1] + inset
        c.line(x1, y1 + inset, x2, y2 + inset)
        mid_x =(x1 + x2)/ 2
        mid_y = (y1 + y2) /2

        c.drawString(x1 - inset / 5  + 50 , mid_y + 10, "Zipper")


    c.showPage()
#     c.save()





# if __name__ == "__main__":
#     cushion_data = {
#         "bottom_width": 57.5,
#         "top_width": 100,
#         "length": 85,
#         "ear":45,
#         "thickness": 2,
#         "height":4,
#         "fill": "DryFast Foam",
#         "piping": "Yes",
#         "ties": "4 Corner ties", #Option : "2 Corner ties bottom width","2 Corner ties top width","2 Side ties-along length","No ties","2 Corner ties","4 Corner ties"
#         "fabric": "Stamskin F430 - 20290 Chalk Blue / Piezo Blue",
#         "zipper": "Bottom Width",#Options: "Top Width","Bottom Width","Ear","Length"
#         "price": "296.55 × 1 = 296.55"
#     }

#     # Define filenames
#     pdf_filename = "t_shape_cushion.pdf"


#     # Create a PDF canvas
#     c = canvas.Canvas(pdf_filename, pagesize=letter)

#     # Call the correctly named function
#     pdf_file = draw_t_shape(c, cushion_data,pdf_filename)

#     try:
#         from google.colab import files
#         files.download(pdf_filename)

#     except ImportError:
#         print(f"PDF saved as {pdf_file}")
   
