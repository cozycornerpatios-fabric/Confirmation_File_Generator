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

def draw_equilateral_triangle(c,cushion):
    page_width, page_height = letter
    cushion_name = cushion.get('cushion_name', 'Equilateral Triangle Cushion')
    side = cushion['side']
    thickness = cushion.get('thickness', 2)
    zipper = cushion.get('zipper', 'None')
    ties = cushion.get('ties', 'None')
    quantity = cushion.get('quantity', 1)
    pipe = cushion.get('pipe', False)
    fill = cushion['fill']
    fabric = cushion['fabric']
   


    c.setFont("Helvetica-Bold", 14)
    y = page_height - inch
    c.drawString(inch, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape", "Equilateral Triangle"),
        ("Side", f"{side} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Zipper", zipper),
        ("Ties", ties),
        ("Piping", "Yes" if pipe else "No"),
        ("Fill", fill),
        ("Fabric Collection", fabric)
   
        


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

    # Scale to fit the page nicely
    scale = (page_width / 3) / side
    side_scaled = side * scale

    # Bottom-left vertex
    x0 = page_width / 2 - side_scaled / 2
    y0 = 1.5 * inch

    # Bottom-right vertex
    x1 = x0 + side_scaled
    y1 = y0

    # Top vertex
    x2 = x0 + side_scaled / 2
    y2 = y0 + (math.sqrt(3)/2) * side_scaled

    # Draw triangle
    c.setStrokeColor(black)
    c.setLineWidth(2)
    p = c.beginPath()
    p.moveTo(x0, y0)
    p.lineTo(x1, y1)
    p.lineTo(x2, y2)
    p.close()
    c.drawPath(p)

    # Side measurement label
    mid_x = (x0 + x1) / 2
    mid_y = (y0 + y1) / 2
    c.setFont("Helvetica", 10)
    c.setStrokeColor(black)
    c.drawString(mid_x - 15, mid_y + 5, f"{side} in")


    # Add piping (blue dashed lines along all sides)
    if pipe == "Yes":
        offset = 7
        c.setStrokeColor(blue)
        c.setDash(4, 4)
        c.line(x0-offset, y0-offset, x1-offset, y1-offset)
        c.line(x1+offset, y1-5, x2+offset, y2-5)
        c.line(x2-offset, y2, x0-offset, y0)
        c.setDash()  # reset dash
      # Piping tie points
        p_x0, p_y0 = x0 - 5, y0 - 5
        p_x1, p_y1 = x1 + 5, y1 - 5
        p_x2, p_y2 = x2, y2 + 5
    else:
        # No piping, so use main vertices
        p_x0, p_y0 = x0, y0
        p_x1, p_y1 = x1, y1
        p_x2, p_y2 = x2, y2   

    # Thickness labeling
    c.setFont("Helvetica", 10)
    c.setStrokeColor(red)
    c.setLineWidth(1)
    
    c.drawString(x1 + 25, y1 + 25, f"Thickness: {thickness} in")

    # Zipper (solid line along left side or specified side)
    if zipper == "side":
        c.setStrokeColor(red)
        c.setLineWidth(1.5)
        c.line(x0 - 10, y0, x2 - 10, y2)
        c.setFont("Helvetica", 10)
        c.setFillColor(red)
        c.drawString((x0 + x2)/2 - 40, (y0 + y2)/2, "Zipper")

    # Ties as short lines
    def draw_tie_line(xc, yc, direction):
        offset = 15  # length of each arm of the V
        c.setStrokeColor(green)
        c.setLineWidth(1.2)
        c.setFont("Helvetica", 8)
        c.setFillColor(green)

        if direction == "up":
            # V pointing upwards
            c.line(xc, yc, xc - offset / 2, yc + offset)
            c.line(xc, yc, xc + offset / 2, yc + offset)
            c.drawString(xc-offset , yc+20, "Ties")
      
        elif direction == "down":
            # V pointing downwards
            c.line(xc, yc, xc - offset / 2, yc - offset)
            c.line(xc, yc, xc + offset / 2, yc - offset)
            c.drawString(xc , yc-offset-10, "Ties")
      
        elif direction == "left":
            # V pointing left
            c.line(xc, yc, xc - offset, yc + offset / 2)
            c.line(xc, yc, xc - offset, yc - offset / 2)
            c.drawString(xc-offset-10 , yc-offset+10, "Ties")
      
        elif direction == "right":
            # V pointing right
            c.line(xc, yc, xc + offset, yc + offset / 2)
            c.line(xc, yc, xc + offset, yc - offset / 2)
            
            c.drawString(xc+10 , yc-offset+10, "Ties")
      
     # Tie attachment points: use piping or main edge
    def get_tie_point(x, y,px,py):
        if pipe:
            # Apply the same offset as used for piping so ties align to blue line
            return (px, py)
        else:
            return (x, y)
   

    if ties == "No Ties":
        pass
    elif ties == "2 Corner Ties":
        x0,y0 = get_tie_point(x0, y0, p_x0, p_y0)
        x1,y1 = get_tie_point(x1, y1, p_x1, p_y1)
        draw_tie_line(x0, y0, "left")
        draw_tie_line(x1, y1, "right")
    elif ties == "2 Side Ties":
        if pipe:
            p1 = (
                p_x0 + (p_x1 - p_x0) * 0.25,
                p_y0 + (p_y1 - p_y0) * 0.25
            )
            p2 = (
                p_x0 + (p_x1 - p_x0) * 0.75,
                p_y0 + (p_y1 - p_y0) * 0.75
            ) 
        else:       
            p1 = (
                x0 + (x1 - x0) * 0.25,
                y0 + (y1 - y0) * 0.25
            )
            p2 = (
                x0 + (x1 - x0) * 0.75,
                y0 + (y1 - y0) * 0.75
            )
        draw_tie_line(*p1, "down")
        draw_tie_line(*p2, "down")
    elif ties == "3 Corner Ties":
        x0, y0 = get_tie_point(x0, y0, p_x0, p_y0)
        x1, y1 = get_tie_point(x1, y1, p_x1, p_y1,)
        x2, y2 = get_tie_point(x2, y2, p_x2, p_y2)
        draw_tie_line(x0, y0, "down")
        draw_tie_line(x1, y1, "down")
        draw_tie_line(x2, y2, "up")

    c.showPage()
#     c.save()
#     return pdf_filename


# if __name__ == "__main__":
#     cushion_data = {
#         "cushion_name": "Equilateral Triangle Cushion",
#         "side": 10,
#         "thickness": 2,  # "2" or "3
#         "zipper": "side",  # or "side"
#         "pipe" :"Yes",
#         "zipper": "side",  # or "side"
#         "ties": "2 Side Ties",  # "2 Corner Ties","2 Side Ties","3 Corner Ties","No Ties"
#         "fabric": "Stamskin F430 - 20290 Chalk Blue / Piezo Bluedfffffffffffffffffffffffffffffffffffffffffffffffffffffffffd",
#         "fill": "DryFast Foam",
#         "price": "296.55 × 1 = 296.55",
#         "quantity": 1
#     }

#     pdf_filename = "equilateral_triangle_cushion.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     pdf_file = draw_equilateral_triangle(c, cushion_data, pdf_filename)

#     # Add this line to save the PDF

#     try:
#         from google.colab import files
#         files.download(pdf_filename)
#     except ImportError:
#         print(f"PDF saved as {pdf_file}")
