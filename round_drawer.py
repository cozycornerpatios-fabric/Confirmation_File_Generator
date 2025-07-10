from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, blue, green
from math import pi, cos, sin

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


def draw_round(c, cushion):
    page_width, page_height = letter

    cushion_name = cushion.get('cushion_name', 'Round Cushion')
    diameter_in = cushion['diameter']
    thickness = cushion['thickness']
    fill = cushion['fill']
    fabric = cushion['fabric']
    # Convert zipper to string
    zipper_on = str(cushion['zipper'])
    piping = cushion.get('piping', 'No')
    quantity = cushion.get('quantity', 1)
    ties = cushion.get('ties')

    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape", "Round"),
        ("Diameter", f"{diameter_in} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Fill", fill),
        ("Fabric", fabric),
        ("Zipper Position", zipper_on),
        ("Piping", piping),
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

    # Draw diagram
    diagram_size = min(page_width / 2.2, page_height / 2.5)
    scale_factor = diagram_size / diameter_in
    radius = (diameter_in * scale_factor) / 2
    center_x = page_width / 2
    center_y = page_height / 2.8

    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.circle(center_x, center_y, radius)

    c.setStrokeColor(black)
    c.setDash(2, 2)
    c.setLineWidth(1)
    c.line(center_x - radius, center_y, center_x + radius, center_y)
    c.setDash([])  # Reset dash style

    # Label diameter above the line
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(center_x, center_y + 12, f"Diameter = {diameter_in}\"")

    piping_margin_in = 0.5
    piping_radius = (diameter_in* scale_factor) / 2 + 10

        # Draw piping (if applicable)
    if piping.lower() in ["yes", "piping"]:
        c.setStrokeColor(blue)
        c.setLineWidth(1)
        c.circle(center_x, center_y, piping_radius)

        # Label for piping
        c.setFont("Helvetica", 10)
        c.setFillColor(blue)
        c.drawString(center_x + piping_radius, center_y - piping_radius/2, "Piping")

    def draw_tie(x, y, angle):
      c.setStrokeColor(green)
      c.setLineWidth(1)
      tie_length = 45
      offset = 0.3  # radians ~17°
      x1 = x + tie_length * cos(angle + offset)
      y1 = y + tie_length * sin(angle + offset)
      x2 = x + tie_length * cos(angle - offset)
      y2 = y + tie_length * sin(angle - offset)
      c.line(x, y, x1, y1)
      c.line(x, y, x2, y2)
      c.setFont("Helvetica", 10)
      c.setFillColor(green)
      c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2, "Tie")


    def draw_fixed_back_tie(x, y):
      c.setStrokeColor(green)
      c.setLineWidth(1)
      tie_length = 30
      offset = 0.8
      x1 = x - tie_length * cos(offset)
      y1 = y - tie_length * sin(offset)
      x2 = x + tie_length * cos(-offset)
      y2 = y - tie_length * sin(offset)
      c.line(x, y, x1, y1)
      c.line(x, y, x2, y2)
      c.setFont("Helvetica", 10)
      c.setFillColor(green)
      c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2, "Tie")

    ties_map = {
    "4 Ties Evenly Spaced": [pi/4, 3*pi / 4, 5*pi / 4, 7* pi / 4],
    "2 Middle Ties": [0, pi]
    }

    tie_radius = piping_radius if piping.lower() in ["yes", "piping"] else radius

    if ties == "2 Back Ties":
        # Manually place two fixed ties along back edge
        draw_fixed_back_tie(center_x - radius / 2, center_y - radius / 4)
        draw_fixed_back_tie(center_x + radius / 2, center_y - radius / 4)

    elif ties in ties_map:
        angles = ties_map[ties]
        for angle in angles:
            x = center_x + tie_radius * cos(angle)
            y = center_y + tie_radius * sin(angle)
            draw_tie(x, y, angle)






    # Thickness label
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawRightString(center_x - radius - 50, center_y - radius/2, f"Thickness = {thickness}\"")
   # zipper
    if(zipper_on):
      arc_angle = 2 * pi / 3  # 120 degrees
      start_angle = pi / 6    # center arc at the top-right quadrant
      arc_points = 30
      arc_radius = radius + 25

      c.setStrokeColor(red)
      c.setLineWidth(2)

      prev_x = None
      prev_y = None
      for i in range(arc_points + 1):
          angle = start_angle + (arc_angle * i / arc_points)
          x = center_x + arc_radius * cos(angle)
          y = center_y + arc_radius * sin(angle)
          if prev_x is not None:
              c.line(prev_x, prev_y, x, y)
          prev_x, prev_y = x, y

      # Label for zipper
      label_x = center_x + arc_radius * cos(start_angle + arc_angle / 2)
      label_y = center_y + arc_radius * sin(start_angle + arc_angle / 2) + 10
      c.setFont("Helvetica", 10)
      c.setFillColor(red)
      c.drawCentredString(label_x, label_y, "Zipper (1/3 Side)")

  # Determine radius for tie placement


    c.showPage()


# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     from math import pi, cos, sin
#     import os

#     test_cushion = {
#         "cushion_name": "Test Cushion - 2 Same Side Long",
#         # "length": 73,
#         # "width": 18,
#         # "height": 3,
#         # "top_width": 17.5,
#         # "bottom_width": 37,
#         # "ear": 17.5,
#         "fill": "Poly Fiber",
#         "fabric": "Outdoor Canvas ",
#         "zipper": 1,
#         "piping": "no",
#         "ties": "4 Ties Evenly Spaced",  # Try with "2 Same Side Short"
#         "quantity": 1,
#         "diameter" : 100,
#         "thickness" : 10
#     }

#     pdf_filename = "test_output.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     draw_round(c, test_cushion)
#     c.save()

#     # Force download link for Colab
#     try:
#         from google.colab import files
#         files.download(pdf_filename)
#     except ImportError:
#         print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
