from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue, green

def draw_rectangle(c, cushion):
    page_width, page_height = letter
    if 'zipper' not in cushion:
            # This part of the code will not be reached because the function is designed to generate PDFs,
            # not return Flask responses. However, I will keep the logic here to illustrate the intended check.
            # return jsonify({"error": "Zipper position is required for all cushions."}), 400
            print("Error: Zipper position is required for all cushions.")
            return

    cushion_name = cushion.get('cushion_name', 'Cushion Specifications')
    length_in = cushion['length']
    width_in = cushion['width']
    thickness = cushion['thickness']
    fill = cushion['fill']
    fabric = cushion['fabric']
    zipper_on = cushion['zipper']
    piping = cushion.get('piping', 'No')
    ties = cushion.get('ties', 'None')
    quantity = cushion.get('quantity', 1)
    tie_offset_from_corner = cushion.get('tie_offset_from_corner', 4)  # default to 4 inches
    short_side_length = min(length_in, width_in)
    long_side_length = max(length_in, width_in)



    # if not isinstance(tie_offset_from_corner, (int, float)) or tie_offset_from_corner < 0:
    #     # return jsonify({"error": f"Invalid tie_offset_from_corner: must be a non-negative number."}), 400
    #     print(f"Error: Invalid tie_offset_from_corner: must be a non-negative number.")
    #     return
    # if tie_offset_from_corner >= short_side_length / 2:
    #     # return jsonify({"error": f"tie_offset_from_corner too large: must be less than half of the short side length ({short_side_length / 2} inches)."}), 400
    #     print(f"Error: tie_offset_from_corner too large: must be less than half of the short side length ({short_side_length / 2} inches).")
    #     return
    if ties in ["2 Side", "2 Side Short"]:
        tie_offset_from_corner = max(tie_offset_from_corner,short_side_length / 2)
    elif ties == "2 Side Long":
        tie_offset_from_corner = max(long_side_length / 2,tie_offset_from_corner)
    elif ties in ["2 Same Side Long", "2 Same Side Short"]:
        tie_offset_from_corner = max(0,tie_offset_from_corner) # 20% or 4 inches max
    else:
        tie_offset_from_corner = max(4,tie_offset_from_corner) # fallback default






    is_zipper_on_long = zipper_on == "Long Side"
    horizontal_side_in = max(length_in, width_in) if is_zipper_on_long else min(length_in, width_in)
    vertical_side_in = min(length_in, width_in) if is_zipper_on_long else max(length_in, width_in)

    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        ("Shape", "Rectangle"),
        ("Length", f"{length_in} inches"),
        ("Width", f"{width_in} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Fill", fill),
        ("Fabric", fabric),
        ("Zipper Position", zipper_on),
        ("Piping", piping),
        ("Ties", ties)

    ]

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(left_x + 120, y, value)
        y -= 0.3 * inch

    diagram_width = page_width / 2.0
    diagram_height = page_height / 3.0
    scale_factor = min(diagram_width / horizontal_side_in, diagram_height / vertical_side_in)
    horizontal_side = horizontal_side_in * scale_factor
    vertical_side = vertical_side_in * scale_factor
    tie_offset = tie_offset_from_corner * scale_factor

    x_origin = (page_width - horizontal_side) / 2
    y_origin = 1.2 * inch
    piping_margin = 0.1 * inch if piping.lower() in ["yes", "piping"] else 0

    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(x_origin, y_origin, horizontal_side, vertical_side)

    # Draw thickness label to the left of the diagram
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawRightString(x_origin - 0.15 * inch - 40, y_origin + vertical_side / 2, f"thickness = {thickness}\"")


    if piping.lower() in ["yes", "piping"]:
        c.setStrokeColor(blue)
        c.setLineWidth(1)
        c.rect(x_origin - piping_margin, y_origin - piping_margin,
                horizontal_side + 2 * piping_margin, vertical_side + 2 * piping_margin)
        c.setFillColor(blue)
        c.setFont("Helvetica", 10)
        label_x = x_origin + horizontal_side + piping_margin + 0.1 * inch + 10
        label_y = y_origin + vertical_side + piping_margin - 0.15 * inch
        c.drawString(label_x, label_y, "Piping")
        c.setStrokeColor(blue)
        c.line(x_origin + horizontal_side + piping_margin, y_origin + vertical_side + piping_margin, label_x - 4, label_y + 4)

    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(x_origin + horizontal_side / 2, y_origin + vertical_side - 12, f"{horizontal_side_in}\"")
    c.drawCentredString(x_origin + 0.2 * inch, y_origin + vertical_side / 2, f"{vertical_side_in}\"")

    c.setStrokeColor(red)
    c.setLineWidth(2)
    zipper_y = y_origin + vertical_side + 0.1 * inch + 6
    c.line(x_origin, zipper_y, x_origin + horizontal_side, zipper_y)
    c.setFillColor(red)
    c.drawString(x_origin + horizontal_side / 2 - 0.2 * inch, zipper_y + 0.1 * inch, "Zipper")

    # Draw ties
    c.setStrokeColor(green)
    c.setLineWidth(1.2)
    tie_len = 0.3 * inch

    def draw_tie(x, y, direction, orientation='horizontal'):
        if orientation == 'horizontal':
            if direction == 'left':
                c.line(x, y, x - tie_len, y - tie_len)
                c.line(x, y, x - tie_len, y + tie_len)
                label_x = x - tie_len - 10
                label_y = y
                # Draw label
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, "Tie")
            elif direction == 'right':
                c.line(x, y, x + tie_len, y - tie_len)
                c.line(x, y, x + tie_len, y + tie_len)
                label_x = x + tie_len + 2
                label_y = y
                # Draw label
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, "Tie")
        elif orientation == 'vertical':
            if direction == 'down':
                c.line(x, y, x - tie_len, y - tie_len)
                c.line(x, y, x + tie_len, y - tie_len)
                label_x = x
                label_y = y - tie_len - 8
                # Draw label
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, "Tie")
            elif direction == 'up':
                c.line(x, y, x - tie_len, y + tie_len)
                c.line(x, y, x + tie_len, y + tie_len)
                label_x = x
                label_y = y + tie_len + 2
                # Draw label
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, "Tie")




    if ties.lower() != "none":
        short_side_is_vertical = vertical_side < horizontal_side
        xo = x_origin - piping_margin
        yo = y_origin - piping_margin
        hs = horizontal_side + 2 * piping_margin
        vs = vertical_side + 2 * piping_margin

        if ties == "4 Short Sides" or ties=="4 Side":
            if short_side_is_vertical:
                draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                draw_tie(xo + hs, yo + tie_offset, 'right', 'horizontal')
                draw_tie(xo + hs, yo + vs - tie_offset, 'right', 'horizontal')
                c.setDash(1, 2)
                c.line(xo - 10,yo,xo-10,yo + tie_offset)
                c.line(xo + hs + 10,yo,xo + hs + 10,yo + tie_offset)
                c.line(xo - 10,yo + vs,xo-10,yo + vs - tie_offset)
                c.line(xo + hs + 10,yo + vs,xo + hs + 10,yo + vs - tie_offset)
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                if(tie_offset>0):
                        c.drawString(xo - 30, yo + tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs + 20, yo + tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo - 30, yo + vs - tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs + 20, yo + vs - tie_offset/2, f" {tie_offset_from_corner}\"")
            else:
                draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                draw_tie(xo + hs - tie_offset, yo, 'down', 'vertical')
                draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')
                c.setDash(1, 2)
                c.line(xo,yo + vs + 10,xo + tie_offset,yo + vs + 10)
                c.line(xo,yo - 10,xo + tie_offset,yo - 10)
                c.line(xo + hs,yo + vs + 10,xo + hs - tie_offset,yo + vs + 10)
                c.line(xo + hs,yo - 10,xo + hs - tie_offset,yo - 10)
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                if(tie_offset>0):
                        c.drawString(xo + tie_offset/2, yo + vs + 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + tie_offset/2, yo - 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs - tie_offset/2, yo + vs + 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs - tie_offset/2, yo - 20, f" {tie_offset_from_corner}\"")

            # c.setFont("Helvetica", 8)
            # c.setFillColor(green)
            # c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")

        elif ties == "4 Long Sides":
            if short_side_is_vertical:
                draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                draw_tie(xo + hs - tie_offset, yo, 'down', 'vertical')
                draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')
                c.setDash(1, 2)
                c.line(xo,yo + vs + 10,xo + tie_offset,yo + vs + 10)
                c.line(xo,yo - 10,xo + tie_offset,yo - 10)
                c.line(xo + hs,yo + vs + 10,xo + hs - tie_offset,yo + vs + 10)
                c.line(xo + hs,yo - 10,xo + hs - tie_offset,yo - 10)
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                if(tie_offset>0):
                        c.drawString(xo + tie_offset/2, yo + vs + 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + tie_offset/2, yo - 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs - tie_offset/2, yo + vs + 20, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs - tie_offset/2, yo - 20, f" {tie_offset_from_corner}\"")
            else:
                draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                draw_tie(xo + hs, yo + tie_offset, 'right', 'horizontal')
                draw_tie(xo + hs, yo + vs - tie_offset, 'right', 'horizontal')
                c.setDash(1, 2)
                c.line(xo - 10,yo,xo-10,yo + tie_offset)
                c.line(xo + hs + 10,yo,xo + hs + 10,yo + tie_offset)
                c.line(xo - 10,yo + vs,xo-10,yo + vs - tie_offset)
                c.line(xo + hs + 10,yo + vs,xo + hs + 10,yo + vs - tie_offset)
                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                if(tie_offset>0):
                        c.drawString(xo - 30, yo + tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs + 20, yo + tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo - 30, yo + vs - tie_offset/2, f" {tie_offset_from_corner}\"")
                        c.drawString(xo + hs + 20, yo + vs - tie_offset/2, f" {tie_offset_from_corner}\"")

            # c.setFont("Helvetica", 8)
            # c.setFillColor(green)
            # c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")

        elif ties == "4 Corners":
            draw_tie(xo, yo, 'left', 'horizontal')
            draw_tie(xo, yo + vs, 'left', 'horizontal')
            draw_tie(xo + hs, yo, 'right', 'horizontal')
            draw_tie(xo + hs, yo + vs, 'right', 'horizontal')

        elif ties == "2 Backside":
            tie_offset_length = cushion.get("tie_offset_length", None)
            tie_offset_width = cushion.get("tie_offset_width", None)

            if tie_offset_length is not None and isinstance(tie_offset_length, (int, float)) and 0 <= tie_offset_length <= vertical_side_in:
                length_offset_scaled = tie_offset_length * scale_factor
            else:
                length_offset_scaled = vertical_side / 2  # Default center if not provided or invalid

            if tie_offset_width is not None and isinstance(tie_offset_width, (int, float)) and 0 <= tie_offset_width <= horizontal_side_in:
                width_offset_scaled = tie_offset_width * scale_factor
            else:
                width_offset_scaled = horizontal_side / 2  # Default center if not provided or invalid

            draw_tie(x_origin + width_offset_scaled, y_origin + length_offset_scaled, 'down', 'vertical')
            draw_tie(x_origin + horizontal_side -  width_offset_scaled, y_origin + length_offset_scaled, 'down', 'vertical')
            c.setFont("Helvetica", 8)
            c.setFillColor(green)
            c.setDash(1, 2)
            c.line(x_origin,y_origin + length_offset_scaled,x_origin + width_offset_scaled,y_origin + length_offset_scaled)
            c.line(x_origin + width_offset_scaled ,y_origin,x_origin + width_offset_scaled,y_origin + length_offset_scaled)
            c.line(x_origin + horizontal_side - width_offset_scaled,y_origin + length_offset_scaled,x_origin + horizontal_side,y_origin + length_offset_scaled)
            c.line(x_origin + horizontal_side -  width_offset_scaled,y_origin,x_origin + horizontal_side -  width_offset_scaled ,y_origin + length_offset_scaled)
            c.setDash([])
            c.drawString(x_origin + width_offset_scaled/2, y_origin + length_offset_scaled + 10 , f"{tie_offset_width}\"")
            c.drawString(x_origin + width_offset_scaled + 10, y_origin + length_offset_scaled/2, f"{tie_offset_length}\"")
            c.drawString(x_origin + horizontal_side - width_offset_scaled/2, y_origin + length_offset_scaled + 10 , f"{tie_offset_width}\"")
            c.drawString(x_origin + horizontal_side - width_offset_scaled - 10, y_origin + length_offset_scaled/2, f"{tie_offset_length}\"")

        elif ties == "2 Short Sides":
            if is_zipper_on_long:
               # zipper on short → vertical → place ties left vertical
                draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                c.setDash(1, 2)
                c.line(xo - 10, yo, xo - 10, yo + tie_offset)
                c.line(xo - 10, yo + vs, xo - 10, yo + vs - tie_offset)
                if(tie_offset>0):
                    c.drawString(xo - 30, yo + tie_offset / 2, f"{tie_offset_from_corner}\"")
                    c.drawString(xo - 30, yo + vs - tie_offset / 2, f"{tie_offset_from_corner}\"")
            else:
                 # zipper on long → horizontal → place ties top horizontal
                draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')
                c.setDash(1, 2)
                c.line(xo, yo + vs + 10, xo + tie_offset, yo + vs + 10)
                c.line(xo + hs, yo + vs + 10, xo + hs - tie_offset, yo + vs + 10)
                if(tie_offset>0):
                    c.drawString(xo + tie_offset / 2, yo + vs + 20, f"{tie_offset_from_corner}\"")
                    c.drawString(xo + hs - tie_offset / 2, yo + vs + 20, f"{tie_offset_from_corner}\"")


        elif ties == "2 Long Side":
            if is_zipper_on_long:
                # zipper on long → horizontal → place ties top horizontal
                draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')
                c.setDash(1, 2)
                c.line(xo, yo + vs + 10, xo + tie_offset, yo + vs + 10)
                c.line(xo + hs, yo + vs + 10, xo + hs - tie_offset, yo + vs + 10)
                if(tie_offset>0):
                    c.drawString(xo + tie_offset / 2, yo + vs + 20, f"{tie_offset_from_corner}\"")
                    c.drawString(xo + hs - tie_offset / 2, yo + vs + 20, f"{tie_offset_from_corner}\"")
            else:
                # zipper on short → vertical → place ties left vertical
                draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                c.setDash(1, 2)
                c.line(xo - 10, yo, xo - 10, yo + tie_offset)
                c.line(xo - 10, yo + vs, xo - 10, yo + vs - tie_offset)
                if(tie_offset>0):
                    c.drawString(xo - 30, yo + tie_offset / 2, f"{tie_offset_from_corner}\"")
                    c.drawString(xo - 30, yo + vs - tie_offset / 2, f"{tie_offset_from_corner}\"")

        elif ties == "2 Corners":
          if is_zipper_on_long:
            draw_tie(xo , yo + vs, 'left', 'horizontal')
            draw_tie(xo , yo , 'left', 'horizontal')

          else:
            draw_tie(xo + hs, yo + vs, 'up', 'vertical')
            draw_tie(xo , yo + vs , 'up', 'vertical')




    c.showPage()

# if __name__ == "__main__":
#     from reportlab.pdfgen import canvas
#     from reportlab.lib.pagesizes import letter
#     import os

#     test_cushion = {
#         "cushion_name": "Test Cushion - 2 Same Side Long",
#         "length": 24,
#         "width": 18,
#         "thickness": 3,
#         "fill": "Poly Fiber",
#         "fabric": "Outdoor Canvas",
#         "zipper": "Long Side",
#         "piping": "Yes",
#         "ties": "2 Corners",  # Try with "2 Same Side Short"
#         "quantity": 1
#     }

#     pdf_filename = "test_output.pdf"
#     c = canvas.Canvas(pdf_filename, pagesize=letter)
#     draw_rectangle(c, test_cushion)
#     c.save()

#     # Force download link for Colab
#     try:
#         from google.colab import files
#         files.download(pdf_filename)
#     except ImportError:
#         print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")
