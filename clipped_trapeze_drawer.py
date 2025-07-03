from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue, green
import uuid
import math

def draw_clipped_trapeze(c,cushion): 
    cushion_name = cushion.get('cushion_name', 'Cushion Specifications')
    bottom_width = cushion["bottom_width"]
    top_width = cushion["top_width"]
    height_in = cushion["height"]
    if(top_width > bottom_width):
        top_width, bottom_width = bottom_width, top_width

    edge = cushion.get("edge", 4)
    thickness = cushion["thickness"]
    fill = cushion.get("fill", "Foam")
    fabric = cushion.get("fabric", "Canvas")
    zipper_position = cushion["zipper"]
    piping = cushion["piping"]
    ties = cushion["ties"]
    quantity = cushion.get('quantity', 1)


    # Derived values
    offset = (bottom_width - top_width) / 2
    # max_draw_height = 4.25 * inch
    # max_draw_width = 3.5 * inch
    # scale = min(max_draw_width / bottom_width, max_draw_height / height_in)

    # b = bottom_width * scale
    # t = top_width * scale
    # h = height_in * scale
    # e = edge * scale
    # o = offset * scale

    # verts = [
    #     (0, 0),
    #     (b, 0),
    #     (b, e),
    #     (o + t, h),
    #     (o, h),
    #     (0, e)
    # ]

    filename = f"confirmation_{uuid.uuid4().hex}.pdf"
    width, height = letter

    # Title and specs
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, height - 1 * inch, "CONFIRMATION - CLIPPED TRAPEZOID")

    specs = [
        f"Bottom Width: {bottom_width} in",
        f"Top Width: {top_width} in",
        f"Height: {height_in} in",
        f"Clipping Edge: {edge} in",
        f"Thickness: {thickness} in",
        f"Fill: {fill}",
        f"Fabric: {fabric}",
        f"Zipper:  {zipper_position}",
        f"Piping: {piping}",
        f"Ties: {ties}",

    ]

    y = height - 1.5 * inch
    for s in specs:
        c.setFont("Helvetica", 10)
        c.drawString(1 * inch, y, s)
        y -= 0.3 * inch

    # # Origin shift
    # x0 = (width - b) / 2
    # y0 = (height - h) / 2

    # Define printable area
    # margin = 0.75 * inch
    # usable_width = width - 2 * margin
    # usable_height = height - 4 * inch
    # leave room for specs text
    # Scale diagram to fit within usable area (with some padding)
    # padding_x = 1.0 * inch  # horizontal padding
    # padding_y = 1.5 * inch  # vertical padding to account for labels
    # usable_width = width - 2 * padding_x
    # usable_height = height - 2 * padding_y
    # # Scale diagram to fit
    # max_cushion_width = bottom_width
    # max_cushion_height = height_in
    # scale_x = usable_width / max_cushion_width
    # scale_y = usable_height / max_cushion_height
    # scale = min(scale_x, scale_y)

    # # Apply scale
    # b = bottom_width * scale
    # t = top_width * scale
    # h = height_in * scale
    # e = edge * scale
    # o = (bottom_width - top_width) / 2 * scale
    # Compute space below specs
    padding_x = 1.0 * inch
    diagram_bottom = 0.5 * inch  # bottom margin
    diagram_top = y - 0.25 * inch  # just below specs text
    usable_height = diagram_top - diagram_bottom
    usable_width = width - 2 * padding_x

    # Compute scale
    scale_x = usable_width / bottom_width
    scale_y = usable_height / height_in
    scale = min(scale_x, scale_y)

    # Apply scale
    b = bottom_width * scale
    t = top_width * scale
    h = height_in * scale
    e = edge * scale
    o = (bottom_width - top_width) / 2 * scale

    # Position diagram at bottom margin
    x0 = (width - b) / 2
    y0 = diagram_bottom

    # Update verts
    verts = [
        (0, 0),
        (b, 0),
        (b, e),
        (o + t, h),
        (o, h),
        (0, e)
    ]

    # Main black shape
    c.setStrokeColor(black)
    c.setLineWidth(1)
    main_path = c.beginPath()
    main_path.moveTo(x0 + verts[0][0], y0 + verts[0][1])
    for x, y_ in verts[1:]:
        main_path.lineTo(x0 + x, y0 + y_)
    main_path.close()
    c.drawPath(main_path)

    # Add thickness text to the left of the diagram
    c.setFont("Helvetica", 8)
    c.drawString(x0 - 1 * inch, y0 + h / 2, f"Thickness = {thickness} in")

    tie_anchor_pts = [(x0 + x, y0 + y) for x, y in verts]

    # Draw piping if requested
    if piping.lower() == "yes":
        def unit_normal(p1, p2):
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.hypot(dx, dy)
            return (-dy / length, dx / length)

        normals = []
        n = len(tie_anchor_pts)
        for i in range(n):
            p_prev = tie_anchor_pts[i - 1]
            p_curr = tie_anchor_pts[i]
            p_next = tie_anchor_pts[(i + 1) % n]
            n1 = unit_normal(p_prev, p_curr)
            n2 = unit_normal(p_curr, p_next)
            avg_nx = (n1[0] + n2[0]) / 2
            avg_ny = (n1[1] + n2[1]) / 2
            length = math.hypot(avg_nx, avg_ny)
            normals.append((avg_nx / length, avg_ny / length))

        offset_amt = 5
        piping_path = c.beginPath()
        for i, (x, y) in enumerate(tie_anchor_pts):
            nx, ny = normals[i]
            offset_x = x + offset_amt * nx
            offset_y = y + offset_amt * ny
            if i == 0:
                piping_path.moveTo(offset_x, offset_y)
            else:
                piping_path.lineTo(offset_x, offset_y)
        piping_path.close()

        c.setStrokeColor(blue)
        c.setLineWidth(0.5)
        c.drawPath(piping_path, stroke=1, fill=0)

        c.setFont("Helvetica", 7)
        c.setFillColor(black)
        top_x = x0 + o + t / 2
        top_y = y0 + h
        c.line(top_x, top_y, top_x + 40, top_y + 10)
        c.drawString(top_x + 42, top_y + 10, "Piping")

    # Draw center height dotted line
    c.setDash(1, 2)
    mid_x = x0 + o + t / 2
    c.line(mid_x, y0, mid_x, y0 + h)
    c.setDash()

    # Dimension labels
    c.setFont("Helvetica", 8)
    angled_len = round(((edge ** 2 + ((bottom_width - top_width) / 2) ** 2) ** 0.5), 2)
    c.drawString(x0 + b / 2 - 14, y0 + 4, f"{bottom_width} in")
    c.drawString(x0 + o + t / 2 - 14, y0 + h - 9, f"{top_width} in")
    c.drawString(x0 + o/2 + o/3, y0 + e + (h - e) / 2, f"{angled_len} in")
    c.drawString(x0 + b - o, y0 + e + (h - e) / 2, f"{angled_len} in")
    c.drawString(mid_x + 5, y0 + h / 2, f"{height_in} in")
    c.drawString(x0 + 10, y0 + e/2, f"{edge} in")
    c.drawString(x0 + b - 18, y0 + e/2, f"{edge} in")

    # Ties logic
    tie_map = {}

    if "2 back" in ties.lower():
        # Place ties along bottom edge, evenly spaced
        tie1_x = x0 + b / 3
        tie2_x = x0 + 2 * b / 3
        tie_y = y0  # at the bottom edge

        tie_map["2 back"] = [
            (tie1_x, tie_y),
            (tie2_x, tie_y)
    ]


    if "2 corner" in ties.lower():
        tie_map["2 corner"] = [tie_anchor_pts[4], tie_anchor_pts[3]]

    if "2 side" in ties.lower():
        # Midpoint of right angled side (between points 2 and 3)
        mid1_x = (tie_anchor_pts[2][0] + tie_anchor_pts[3][0]) / 2
        mid1_y = (tie_anchor_pts[2][1] + tie_anchor_pts[3][1]) / 2

        # Midpoint of left angled side (between points 5 and 4)
        mid2_x = (tie_anchor_pts[5][0] + tie_anchor_pts[4][0]) / 2
        mid2_y = (tie_anchor_pts[5][1] + tie_anchor_pts[4][1]) / 2

        tie_map["2 side"] = [
            (mid1_x, mid1_y),
            (mid2_x, mid2_y)
      ]


    if "4 corner" in ties.lower():
        tie_map["4 corner"] = [tie_anchor_pts[0], tie_anchor_pts[1], tie_anchor_pts[4], tie_anchor_pts[3]]

    def draw_down_v_fork(x, y):
        dx = 0.2 * inch
        dy = 0.2 * inch
        c.line(x, y, x - dx, y - dy)
        c.line(x, y, x + dx, y - dy)

    def draw_tie_fork(x, y, up=True):
        dx = 0.2 * inch
        dy = 0.2 * inch
        sign = 1 if up else -1
        c.line(x, y, x - dx, y + sign * dy)
        c.line(x, y, x + dx, y + sign * dy)

    def draw_left(x, y):
        dx = 0.4 * inch
        dy = 0.4 * inch
        c.line(x, y, x - dx, y + dy)
        c.line(x, y, x - dx, y - dy + 5)

    def draw_right(x, y):
        dx = 0.4 * inch
        dy = 0.4 * inch
        c.line(x, y, x + dx, y + dy)
        c.line(x, y, x + dx, y - dy + 5)



    c.setStrokeColor(green)
    c.setFont("Helvetica", 6)
    l = 0
    def draw_tie_and_label(x, y, direction):
        dx = 0.2 * inch
        dy = 0.2 * inch
        c.setStrokeColor(green)
        c.setFillColor(green)
        c.setFont("Helvetica", 6)

        if direction == "down":
            c.line(x, y, x - dx, y - dy)
            c.line(x, y, x + dx, y - dy)
            c.drawString(x - 10, y - dy - 10, "Ties")

        elif direction == "up":
            c.line(x, y, x - dx, y + dy)
            c.line(x, y, x + dx, y + dy)
            c.drawString(x - 10, y + dy + 2, "Ties")

        elif direction == "left":
            c.line(x, y, x - dx, y )
            c.line(x, y, x - dx, y + dy)
            c.drawString(x - dx - 20, y - 3, "Ties")

        elif direction == "right":
            c.line(x, y, x + dx, y +dy)
            c.line(x, y, x + dx, y )
            c.drawString(x + dx + 2, y - 3, "Ties")

    for key, points in tie_map.items():
        for x, y in points:
            if key == "2 back":
                draw_down_v_fork(x, y)
                draw_tie_and_label(x, y, "down")


            elif key == "2 side":
                diagram_mid_x = x0 + b / 2
                if x < diagram_mid_x:
                    draw_tie_and_label(x, y, "left")
                else:
                    draw_tie_and_label(x, y, "right")


            elif key == "2 corner":
                draw_tie_and_label(x, y, "up")

            elif key == "4 corner":
                if (x, y) == tie_anchor_pts[0] or (x, y) == tie_anchor_pts[1]:
                    draw_tie_and_label(x, y, "down")
                elif (x, y) == tie_anchor_pts[3] or (x, y) == tie_anchor_pts[4]:
                    draw_tie_and_label(x, y, "up")
    # Zipper mark
    if zipper_position != "None":

        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.setFillColor(red)
        offset_zipper = 0.1 * inch
        if zipper_position == "long side":
            z1 = verts[0][0], verts[0][1] - offset_zipper
            z2 = verts[1][0], verts[1][1] - offset_zipper
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            c.drawString(x0 + (z1[0] + z2[0]) / 2 - 50 , y0 + (z1[1] + z2[1]) / 2 - 10  - offset_zipper, "Zipper")
        elif zipper_position == "short side":
            z1 = verts[4][0], verts[4][1] + offset_zipper
            z2 = verts[3][0], verts[3][1] + offset_zipper
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            c.drawString(x0 + (z1[0] + z2[0]) / 2 - 50 , y0 + (z1[1] + z2[1]) / 2 + 20  - offset_zipper, "Zipper")
        elif zipper_position == "angle side":
            z1 = verts[0][0] - offset_zipper, verts[0][1]
            z2 = verts[5][0] - offset_zipper, verts[5][1]
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            # c.drawString(x0 + (z1[0] + z2[0]) / 2 - 50 , y0 + (z1[1] + z2[1]) / 2 - 10  - offset_zipper, "Zipper")
            dx=verts[4][0] - verts[5][0]
            dy=verts[4][1] - verts[5][1]
            length = math.hypot(dx, dy)
            nx = -dy / length
            ny = dx / length
            z1 = verts[5][0] + offset_zipper * nx,verts[5][1] + offset_zipper * ny
            z2 = verts[4][0] + offset_zipper * nx,verts[4][1] + offset_zipper * ny
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            c.drawString(x0 + (z1[0] + z2[0]) / 2 - 50 , y0 + (z1[1] + z2[1]) / 2 - 10  - offset_zipper, "Zipper")
        elif zipper_position == "TopPlusAngled":
            z1 = verts[4][0], verts[4][1] + offset_zipper
            z2 = verts[3][0], verts[3][1] + offset_zipper
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            c.drawString(x0 + (z1[0] + z2[0]) / 2 - 50 , y0 + (z1[1] + z2[1]) / 2 + 20  - offset_zipper, "Zipper")
            dx=verts[4][0] - verts[5][0]
            dy=verts[4][1] - verts[5][1]
            length = math.hypot(dx, dy)
            nx = -dy / length
            ny = dx / length
            z1 = verts[5][0] + offset_zipper * nx,verts[5][1] + offset_zipper * ny
            z2 = verts[4][0] + offset_zipper * nx,verts[4][1] + offset_zipper * ny
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])
            z1 = verts[2][0] - offset_zipper * nx,verts[2][1] + offset_zipper * ny
            z2 = verts[3][0] - offset_zipper * nx,verts[3][1] + offset_zipper * ny
            c.line(x0 + z1[0], y0 + z1[1], x0 + z2[0], y0 + z2[1])


        else:
            z1 = verts[0][0], verts[0][1] - offset_zipper
            z2 = verts[1][0], verts[1][1] - offset_zipper
    c.showPage()
