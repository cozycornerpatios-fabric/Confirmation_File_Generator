import os
import uuid
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, purple, green
from google.colab import files



# === DRAW PAGES FOR EACH CUSHION ===
def draw_trapezium(c,cushion):
    page_width, page_height = letter
    top_base_in = cushion['top_base']
    bottom_base_in = cushion['bottom_base']
    height_in = cushion['height']
    zipper_position = cushion['zipper']
    piping = cushion['piping']
    ties_option = cushion['ties']
    tie_offset = cushion.get("tie_offset_from_base", 0)


    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, "Cushion Specifications")
    y -= 0.4 * inch

    shape = "Trapezoid"
    thickness = cushion.get("thickness", "")
    quantity = cushion.get("quantity", 1)

    specs = [
        ("Shape", shape),
        ("Top Base", f"{top_base_in} inches"),
        ("Bottom Base", f"{bottom_base_in} inches"),
        ("Height", f"{height_in} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Zipper Position", zipper_position),
        ("Piping", piping),
        ("Ties", ties_option),
        ("Quantity", str(quantity))
    ]

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(left_x + 130, y, value)
        y -= 0.3 * inch


    # SCALING + POINTS
    max_width = 5 * inch
    max_height = 4 * inch
    scale = min(max_width / bottom_base_in, max_height / height_in)
    top_base = top_base_in * scale
    bottom_base = bottom_base_in * scale
    height = height_in * scale

    x_origin = 1.5 * inch
    y_origin = 2.5 * inch
    top_left = (x_origin + (bottom_base - top_base) / 2, y_origin + height)
    top_right = (top_left[0] + top_base, top_left[1])
    bottom_left = (x_origin, y_origin)
    bottom_right = (x_origin + bottom_base, y_origin)
    mid_left = ((top_left[0] + bottom_left[0]) / 2, (top_left[1] + bottom_left[1]) / 2)
    mid_right = ((top_right[0] + bottom_right[0]) / 2, (top_right[1] + bottom_right[1]) / 2)
    slant_len_in = round(math.hypot((bottom_base_in - top_base_in) / 2, height_in), 2)

    def inset_corner(corner, adj1, adj2, amount):
        dx1, dy1 = adj1[0] - corner[0], adj1[1] - corner[1]
        dx2, dy2 = adj2[0] - corner[0], adj2[1] - corner[1]
        len1, len2 = math.hypot(dx1, dy1), math.hypot(dx2, dy2)
        dx = (dx1 / len1 + dx2 / len2)
        dy = (dy1 / len1 + dy2 / len2)
        norm = math.hypot(dx, dy)
        return (corner[0] + dx / norm * amount, corner[1] + dy / norm * amount)

    inset = 10
    i_tl = inset_corner(top_left, top_right, bottom_left, inset)
    i_tr = inset_corner(top_right, top_left, bottom_right, inset)
    i_br = inset_corner(bottom_right, bottom_left, top_right, inset)
    i_bl = inset_corner(bottom_left, bottom_right, top_left, inset)

    anchor_top_left = top_left if piping == "Yes" else i_tl
    anchor_top_right = top_right if piping == "Yes" else i_tr
    anchor_bottom_left = bottom_left if piping == "Yes" else i_bl
    anchor_bottom_right = bottom_right if piping == "Yes" else i_br
    anchor_mid_left = ((anchor_top_left[0] + anchor_bottom_left[0]) / 2, (anchor_top_left[1] + anchor_bottom_left[1]) / 2)
    anchor_mid_right = ((anchor_top_right[0] + anchor_bottom_right[0]) / 2,
                    (anchor_top_right[1] + anchor_bottom_right[1]) / 2)
    if piping == "Yes":
        tie_top_left = top_left
        tie_top_right = top_right
        tie_bottom_left = bottom_left
        tie_bottom_right = bottom_right
    else:
        tie_top_left = i_tl
        tie_top_right = i_tr
        tie_bottom_left = i_bl
        tie_bottom_right = i_br

    def draw_tie(x, y, direction):
        c.setStrokeColor(green)
        c.setFillColor(green)
        c.setFont("Helvetica", 8)
        v_len = 20
        if direction == "left":
            c.line(x, y, x - v_len, y + v_len)
            c.line(x, y, x - v_len, y - v_len)
            c.drawString(x - v_len - 25, y - 3, "Tie")
        elif direction == "right":
            c.line(x, y, x + v_len, y + v_len)
            c.line(x, y, x + v_len, y - v_len)
            c.drawString(x + v_len, y - 6, "Tie")
        elif direction == "down":
            c.line(x, y, x - v_len, y - v_len)
            c.line(x, y, x + v_len, y - v_len)
            c.drawString(x - 10, y - v_len - 12, "Tie")
        elif direction == "up":
            c.line(x, y, x - v_len, y + v_len)
            c.line(x, y, x + v_len, y + v_len)
            c.drawString(x - 10, y + v_len, "Tie")
            
    def draw_tie_distance_label(x_tie, y_tie, x_ref, y_ref):
        c.setStrokeColor(black)
        c.setDash(3, 3)
        c.line(x_ref, y_ref, x_tie, y_tie)  # Dotted line to show distance
        c.setDash()  # Reset to solid
          


    def draw_ties(opt):
        if opt == "2 Back Ties":
            left_x = bottom_left[0] + (bottom_right[0] - bottom_left[0]) * (tie_offset / bottom_base_in)
            right_x = bottom_right[0] - (bottom_right[0] - bottom_left[0]) * (tie_offset / bottom_base_in)
            y = tie_bottom_left[1]
            draw_tie(left_x, y, "down")
            draw_tie(right_x, y, "down")
            # Label distances
            draw_tie_distance_label(bottom_left[0], y - 50, left_x, y - 50)
            draw_tie_distance_label(bottom_right[0], y - 50, right_x, y - 50)
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawString((bottom_left[0] + left_x) / 2 - 10, (y - 50 + y - 50) / 2 + 5,f"{tie_offset}\"")
            c.drawString((bottom_right[0]+ right_x) / 2 - 10, (y - 50 + y - 50) / 2 + 5,f"{tie_offset}\"")
           

        elif opt == "2 Side Ties":
            # Left side
            dx_left = tie_top_left[0] - bottom_left[0]
            dy_left = tie_top_left[1] - bottom_left[1]
            ratio_left = min(1, tie_offset / slant_len_in)
            x_left = tie_bottom_left[0] + dx_left * ratio_left
            y_left = tie_bottom_left[1] + dy_left * ratio_left
            draw_tie(x_left, y_left, "left")
            draw_tie_distance_label(x_left - 10, y_left, bottom_left[0] - 10, bottom_left[1])
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawString(((x_left - 10 + bottom_left[0]) / 2) - 30, ( y_left +  bottom_left[1]) / 2 + 5,f'{tie_offset}"')
           
            # Right side
            dx_right = top_right[0] - bottom_right[0]
            dy_right = top_right[1] - bottom_right[1]
            ratio_right = min(1, tie_offset / slant_len_in)
            x_right = bottom_right[0] + dx_right * ratio_right
            y_right = bottom_right[1] + dy_right * ratio_right
            draw_tie(x_right, y_right, "right")
            draw_tie_distance_label(x_right +10,y_right,bottom_right[0] + 10,bottom_right[1])
      
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawString((x_right +10 + bottom_right[0]+10) / 2 + 30, ( y_right + bottom_right[1]) / 2 + 5,f'{tie_offset}"')
           
            
        elif opt == "4 Corner Ties":
            draw_tie(tie_bottom_left[0], tie_bottom_left[1], "down")
            draw_tie(tie_bottom_right[0], tie_bottom_right[1], "down")
            draw_tie(tie_top_left[0], tie_top_left[1], "up")
            draw_tie(tie_top_right[0], tie_top_right[1], "up")
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            

           
        elif opt == "2 Corner Ties":
            draw_tie(tie_bottom_left[0], tie_bottom_left[1], "down")
            draw_tie(tie_bottom_right[0], tie_bottom_right[1], "down")  
            


    if piping == "Yes":
        c.setStrokeColor(purple)
        c.setLineWidth(1.6)
        c.lines([
            (top_left[0], top_left[1], top_right[0], top_right[1]),
            (top_right[0], top_right[1], bottom_right[0], bottom_right[1]),
            (bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1]),
            (bottom_left[0], bottom_left[1], top_left[0], top_left[1])
        ])
        c.setFillColor(purple)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(top_right[0] + 30, top_right[1] - 20, "Piping")
        c.line(top_right[0] + 25, top_right[1] - 15, top_right[0] + 5, top_right[1] - 15)

    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.lines([
        (i_tl[0], i_tl[1], i_tr[0], i_tr[1]),
        (i_tr[0], i_tr[1], i_br[0], i_br[1]),
        (i_br[0], i_br[1], i_bl[0], i_bl[1]),
        (i_bl[0], i_bl[1], i_tl[0], i_tl[1])
    ])

    c.setStrokeColor(red)
    c.setLineWidth(1.5)
    c.setFillColor(red)
    c.setFont("Helvetica-Bold", 12)
    if zipper_position == "Top":
        c.line(top_left[0], top_left[1] + 10, top_right[0], top_right[1] + 10)
        c.drawCentredString((top_left[0] + top_right[0]) / 2, top_left[1] + 15, "Zipper")
    elif zipper_position == "Bottom":
        c.line(bottom_left[0], bottom_left[1] - 10, bottom_right[0], bottom_right[1] - 10)
        c.drawCentredString((bottom_left[0] + bottom_right[0]) / 2, bottom_left[1] - 20, "Zipper")
    elif zipper_position == "Left":
        c.line(bottom_left[0] - 10, bottom_left[1], top_left[0] - 10, top_left[1])
        c.drawString(bottom_left[0] - 10, (top_left[1] + bottom_left[1]) / 2 + 20, "Zipper")
    elif zipper_position == "Right":
        c.line(bottom_right[0] + 10, bottom_right[1], top_right[0] + 10, top_right[1])
        c.drawString(bottom_right[0], (top_right[1] + bottom_right[1]) / 2, "Zipper")

    draw_ties(ties_option)

    c.setStrokeColor(black)
    c.setDash(3, 3)
    c.line((i_tl[0] + i_tr[0]) / 2, i_tl[1], (i_bl[0] + i_br[0]) / 2, i_bl[1])
    c.setDash()
    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawCentredString(i_tl[0] + i_tr[0] - 250, i_tl[1] - 10, f'{top_base_in}"')
    c.drawCentredString(i_bl[0] + i_br[0] - 250, i_bl[1] + 10, f'{bottom_base_in}"')
    c.drawCentredString((i_tl[0] + i_tr[0]) / 2 + 20, (i_tl[1] + i_bl[1]) / 2, f'{height_in}"')
    c.drawString(mid_left[0] + 10, mid_left[1] - 5, f'{slant_len_in}"')
    c.drawString(mid_right[0] - 40, mid_right[1] - 5, f'{slant_len_in}"')
    c.drawCentredString((i_tl[0] + i_tr[0]) / 2 + 20, (i_tl[1] + i_bl[1]) / 2, f"{height_in}\"")
    thickness_in = cushion.get('thickness', None)
    c.drawCentredString(
        i_bl[0] - 50,

        (i_tl[1] + i_bl[1]) / 2 - 15,
        f"Thickness: {thickness_in}\""
    )
    c.showPage()
