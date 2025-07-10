from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue,red,green
from math import pi,cos,sin

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

def draw_semi_round(c, cushion):
    page_width, page_height = letter

    cushion_name = cushion.get('cushion_name', 'Semi-Round Cushion')
    diameter_in = cushion['diameter']
    thickness = cushion['thickness']
    piping = cushion.get('piping', 'No')
    quantity = cushion.get('quantity', 1)
    zipper_position = cushion.get('zipper', 'No')
    ties = cushion.get('ties', 'No Ties')
    fabric = cushion.get('fabric', 'Cotton')
    fill = cushion.get('fill', 'None')


    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape", "Semi-Round"),
        ("Diameter", f"{diameter_in} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Piping", piping),
        ("Zipper", zipper_position),
        ("Ties", ties),
        ("Fabric", fabric),
        ("Fill", fill)
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

    # Draw diagram
    diagram_size = min(page_width / 2.2, page_height / 2.5)
    scale_factor = diagram_size / diameter_in
    radius = (diameter_in * scale_factor) / 2
    center_x = page_width / 2
    center_y = page_height / 2.8

    # Semi-circle path
    p = c.beginPath()
    p.moveTo(center_x - radius, center_y)
    p.arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius, 180, -180) # Changed extent from 0 to -180
    p.lineTo(center_x + radius, center_y)
    p.lineTo(center_x - radius, center_y)
    p.close()

    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.drawPath(p, stroke=1, fill=0)

    

    if zipper_position == 'Top Curved':
        c.setStrokeColor(red)
       
        c.setLineWidth(1.2)
        c.arc(center_x - radius - 10, center_y - radius - 10, center_x + radius + 10, center_y + radius + 10, 180, -180)
       

        c.setFont("Helvetica", 10)
        c.setFillColor(red)
        c.drawCentredString(center_x, center_y + radius + 15, "zipper")

    elif zipper_position == 'Bottom Straight':
        c.setStrokeColor(red)
       
        c.setLineWidth(1.2)
        c.line(center_x - radius, center_y - 10, center_x + radius - 5, center_y - 10)
      

        c.setFont("Helvetica", 10)
        c.setFillColor(red)
        c.drawCentredString(center_x, center_y - 20, "zipper")

        

    # Diameter label
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(center_x, center_y + 12, f"Diameter = {diameter_in}\"")

    # Piping (optional)
    if piping.lower() in ["yes", "piping"]:
        piping_radius = ((diameter_in + 5) * scale_factor) / 2  # Offset for visibility
        c.setStrokeColor(blue)
       
        c.setLineWidth(1)

        # Begin path for just the curved edge
        p_piping = c.beginPath()
        p_piping.arc(center_x - piping_radius, center_y - piping_radius,
                    center_x + piping_radius, center_y + piping_radius,
                    180, -180)
        c.line(center_x - piping_radius, center_y - 5, center_x + piping_radius, center_y - 5)
        c.drawPath(p_piping, stroke=1, fill=0)
        
        c.setDash([])  # Reset dash style
        label_x = center_x
        label_y = center_y + piping_radius + 15  # label above arc
        arrow_end_x = center_x
        arrow_end_y = center_y + piping_radius * cos(pi / 2) + piping_radius * sin(pi / 2)

        c.setStrokeColor(blue)
        c.setLineWidth(1)
       
            
        # Piping label along the curved edge
        c.setFont("Helvetica", 10)
        c.setFillColor(blue)
        c.drawString(center_x + piping_radius + 5, center_y+5, "Piping")
    # Tie drawing helper
    def draw_tie(x, y, angle):
        c.setStrokeColor(green)
        c.setLineWidth(1)
        tie_length = 50
        offset = 0.3  # ~17 degree spread
        x1 = x + tie_length * cos(angle + offset)
        y1 = y + tie_length * sin(angle + offset)
        x2 = x + tie_length * cos(angle - offset)
        y2 = y + tie_length * sin(angle - offset)
        c.line(x, y, x1, y1)
        c.line(x, y, x2, y2)
        c.setFont("Helvetica", 10)
        c.setFillColor(green)
        c.drawCentredString((x1 - 10 + x2 + 10) / 2, (y1 + 5 + y2+ 5) / 2 - 10, "Tie")

    # Tie positions map
    ties_map = {
        "2 Curve Edge Ties": [5 * pi / 6, pi / 6],
        "2 Flat Corner Ties": [7 * pi /6, 11 * pi / 6],
        "4 Corner Ties": [5 * pi / 6, pi / 6, 7 * pi / 6, 11 * pi / 6]
    }

        
    # Determine radius for tie attachment
    if piping.lower() in ["yes", "piping"]:
        tie_radius = ((diameter_in + 5) * scale_factor) / 2  # Attach to piping (blue line)
    else:
        tie_radius = radius  # Attach to cushion outline (black line)

    

    if ties in ties_map:
        if ties == "2 Curve Edge Ties":
            # Place ties higher on the curve at 120° and 60°
            angles = [2 * pi / 3, pi / 3]  # 120°, 60°
            for angle in angles:
                x = center_x + tie_radius * cos(angle)
                y = center_y + tie_radius * sin(angle)
                draw_tie(x, y, angle)

        elif ties == "2 Flat Corner Ties":
            draw_tie(center_x - tie_radius, center_y, 7 * pi / 6)
            draw_tie(center_x + tie_radius, center_y, 11 * pi / 6)

        elif ties == "4 Corner Ties":
            angles = [2 * pi / 3, pi / 3]  # 120°, 60°
            for angle in angles:
                x = center_x + tie_radius * cos(angle)
                y = center_y + tie_radius * sin(angle)
                draw_tie(x, y, angle)

                draw_tie(center_x - tie_radius, center_y, 7 * pi / 6)
                draw_tie(center_x + tie_radius, center_y, 11 * pi / 6)

    # Thickness label
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawRightString(center_x - radius - 40, center_y , f"Thickness = {thickness}\"")

    c.showPage()

# from reportlab.pdfgen import canvas

# test_cushion = {
#     "cushion_name": "Semi-Round Cushion",
#     "diameter": 100,
#     "thickness": 10,
#     "piping": "yes",
#     "quantity": 1,
#     "ties":"2 Flat Corner Ties",#Option "4 Corner Ties","2 Flat Corner Ties","2 Curve Edge Ties".
#     "zipper": "Bottom Straight",  # Option: "Bottom Straight", "Top Curved"
#     "fabric": "Cotton",
#     "fill": "None"

# }

# pdf_filename = "test_output.pdf"
# c = canvas.Canvas(pdf_filename, pagesize=letter)
#     # Call the function directly
# draw_semi_round(c,test_cushion)
# c.save()


#  # Force download link for Colab
# try:
#     from google.colab import files
#     files.download(pdf_filename)
# except ImportError:
#     print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
