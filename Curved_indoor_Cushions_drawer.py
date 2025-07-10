from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green
from math import pi, cos, sin

def draw_curved_cushion(c, cushion):
    page_width, page_height = letter

    cushion_name = cushion.get('cushion_name', 'Curved Cushion')
    # inner_radius = cushion['inner_radius']
    # outer_radius = cushion['outer_radius']
    # thickness = cushion['thickness']
    # piping = cushion.get('piping', 'No')
    quantity = cushion.get('quantity', 1)
    # zipper_position = cushion.get('zipper', 'No')
    # ties = cushion.get('ties', 'No Ties')
    # Extract values
      # Extract inputs

    length = cushion['length']
    front_width_straight = cushion['front_width_straight']
    back_width_straight = cushion['back_width_straight']
    front_width_curved = cushion['front_width_curved']
    back_width_curved = cushion['back_width_curved']
    inner_radius = front_width_straight / 2
    outer_radius = back_width_straight / 2
    thickness = cushion['thickness']
    fill = cushion['fill']
    fabric_collection = cushion['fabric_collection']
    fabric_option = cushion['fabric_option']
    piping = cushion['piping']
    # ties = cushion['ties']
    zipper_position = cushion['zipper']
    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Quantity: {quantity})")
    y -= 0.4 * inch

    specs = [
        # ("Shape", "Curved"),
        # ("Inner Radius", f"{inner_radius} inches"),
        # ("Outer Radius", f"{outer_radius} inches"),
        # ("Thickness", f"{thickness} inches"),
        ("Shape", "Curved"),
        ("Length", f"{length} inches"),
        ("Front Width(Straight)", f"{  front_width_straight} inches"),
        ("Back Width(Straight)", f"{  back_width_straight} inches"),
        ("Front Width(Curved)", f"{  front_width_curved} inches"),
        ("Back Width(Curved)", f"{  back_width_curved} inches"),
        ("Thickness", f"{thickness} inches"),
        ("Fill", fill),
        ("Fabric Collection", fabric_collection),
        ("Fabric Option", fabric_option),
        ("Zipper Position", zipper_position),
        ("Piping", piping),
        ("Ties", "None"),
        ("Quantity", str(quantity)),
    ]

    for label, value in specs:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_x, y, f"{label}:")
        c.setFont("Helvetica", 12)
        c.drawString(left_x + 120, y, value)
        y -= 0.3 * inch

    # diagram_size = min(page_width / 2.2, page_height / 2.5)
    # scale_factor = diagram_size / (outer_radius * 2)
    # inner_r = inner_radius * scale_factor
    # outer_r = outer_radius * scale_factor
    # center_x = page_width / 2
    # center_y = page_height / 2.5

    # # --- Set Diagram Area ---
    # margin_x = 1 * inch
    # margin_y = 1 * inch
    # diagram_max_width = page_width - 2 * margin_x
    # diagram_max_height = page_height * 0.25  # Allow 45% of page height for diagram

    # # --- Get Dimensions in inches ---
    # inner_radius_in = front_width_curved / 2
    # outer_radius_in = back_width_curved / 2
    # depth_in = length  # vertical depth

    # # Calculate bounding box size
    # full_width_in = outer_radius_in * 2
    # full_height_in = depth_in

    # # --- Convert to points and scale ---
    # diagram_width_pts = full_width_in * inch
    # diagram_height_pts = full_height_in * inch

    # scale_factor = min(diagram_max_width / diagram_width_pts, diagram_max_height / diagram_height_pts)

    # # Scaled radii and length
    # inner_r = inner_radius_in * inch * scale_factor
    # outer_r = outer_radius_in * inch * scale_factor
    # depth = depth_in * inch * scale_factor

    # # --- Dynamic position: below specs ---
    # text_block_height = len(specs) * 0.3 * inch + 1.5 * inch
    # center_x = page_width / 2
    # center_y = page_height - text_block_height - depth / 2 - 0.4 * inch  # some padding

        # --- Layout Constraints ---
    diagram_margin_bottom = 0.75 * inch
    diagram_margin_top = 0.5 * inch
    margin_bottom = 1 * inch



    # --- Calculate spec block height ---
    # spec_line_height = 0.3 * inch
    # spec_title_height = 0.4 * inch  # padding above and below
    # spec_block_height = len(specs) * spec_line_height + spec_title_height + 1 * inch

    # --- Available height below text ---
    available_height = page_height - diagram_margin_bottom - diagram_margin_top - (page_height - y)

    # --- Diagram physical size (in inches) ---
    outer_radius_in = back_width_curved / 2
    inner_radius_in = front_width_curved / 2
    depth_in = length  # front to back

    # --- Required diagram size in points ---
    diagram_width_pts = outer_radius_in * 2 * inch
    diagram_height_pts = depth_in * inch

    # --- Scale to fit within available space ---
    scale_factor = min((page_width - 2 * inch) / diagram_width_pts,
                      available_height / diagram_height_pts)

    # --- Final scaled dimensions ---
    inner_r = inner_radius_in * inch * scale_factor
    outer_r = outer_radius_in * inch * scale_factor
    depth = depth_in * inch * scale_factor

    # --- Center positions ---

    center_x = page_width / 2
    center_y = diagram_margin_bottom + depth / 2




    segments = 100
    theta_vals = [i * (pi/2) / (segments - 1) for i in range(segments)]
    x_inner = [center_x + inner_r * cos(t) for t in theta_vals]
    y_inner = [center_y + inner_r * sin(t) for t in theta_vals]
    x_outer = [center_x + outer_r * cos(t) for t in theta_vals]
    y_outer = [center_y + outer_r * sin(t) for t in theta_vals]

          # ----------------------------- #
    # 📐 Dimension Arrows + Numbers #
    # ----------------------------- #

    arrow_size = 4
    c.setStrokeColor(black)
    c.setFont("Helvetica", 9)
    c.setFillColor(black)

    # 1. 📏 Length (Vertical arrow on right side)
    # x_pos = x_outer[-1] + 20
    # y_top = y_outer[-1]
    # y_bottom = y_inner[-1]
    # c.line(x_outer[-1], y_top, x_outer[-1], y_bottom)
    # c.line(x_outer[-1], y_top, x_outer[-1] - arrow_size, y_top - arrow_size)
    # c.line(x_outer[-1], y_top, x_outer[-1] + arrow_size, y_top - arrow_size)
    # c.line(x_outer[-1], y_bottom, x_outer[-1] - arrow_size, y_bottom + arrow_size)
    # c.line(x_outer[-1], y_bottom, x_outer[-1] + arrow_size, y_bottom + arrow_size)

    # Label
    mid_l_x = (x_outer[-1] + x_inner[-1]) / 2
    mid_l_y = (y_outer[-1] + y_inner[-1]) / 2
    c.drawString(mid_l_x + 5, mid_l_y - 5, f"{length}\"")

    # 2. 📏 Front Width (Straight) — inner arc bottom
    mid_fw_x = (x_inner[0] + x_inner[-1]) / 2
    mid_fw_y = (y_inner[0] + y_inner[-1]) / 2
    # x_left = x_inner[0]
    # x_right = x_inner[-1]
    # c.line(x_left, fw_y, x_right, fw_y)
    # c.line(x_left, fw_y, x_left + arrow_size, fw_y + arrow_size)
    # c.line(x_left, fw_y, x_left + arrow_size, fw_y - arrow_size)
    # c.line(x_right, fw_y, x_right - arrow_size, fw_y + arrow_size)
    # c.line(x_right, fw_y, x_right - arrow_size, fw_y - arrow_size)
    # c.line(x_left, fw_y, x_left, y_inner[0])
    # c.line(x_right, fw_y, x_right, y_inner[-1])

    # Label
    # c.drawCentredString((x_left + x_right) / 2+5, fw_y + 20, f"{front_width_straight}\"")
    c.drawCentredString(mid_fw_x - 10,mid_fw_y , f"{front_width_straight}\"")


    # 3. 📏 Back Width (Straight) — outer arc top
    # mid_bw_y = y_outer[0] + 20
    # x_left = x_outer[0]
    # x_right = x_outer[-1]
    mid_bw_x = (x_outer[0] + x_outer[-1]) / 2
    mid_bw_y = (y_outer[0] + y_outer[-1]) / 2
    c.drawCentredString(mid_bw_x, mid_bw_y + 12, f"{back_width_straight}\"")
    # c.line(x_left, bw_y, x_right, bw_y)
    # c.line(x_left, bw_y, x_left + arrow_size, bw_y + arrow_size)
    # c.line(x_left, bw_y, x_left + arrow_size, bw_y - arrow_size)
    # c.line(x_right, bw_y, x_right - arrow_size, bw_y + arrow_size)
    # c.line(x_right, bw_y, x_right - arrow_size, bw_y - arrow_size)
    # c.line(x_left, bw_y, x_left, y_outer[0])
    # c.line(x_right, bw_y, x_right, y_outer[-1])

    # Label
    # c.drawCentredString((x_left + x_right) / 2 + 40, bw_y + 20, f"{back_width_straight}\"")

    # Draw arcs
    c.setStrokeColor(black)
    # c.setDash(2,2)
    for i in range(segments - 1):
        c.line(x_inner[i], y_inner[i], x_inner[i+1], y_inner[i+1])


    c.setStrokeColor(black)
    # c.setDash(2,2)
    for i in range(segments - 1):
        c.line(x_outer[i], y_outer[i], x_outer[i+1], y_outer[i+1])

    c.line(x_inner[0], y_inner[0], x_outer[0], y_outer[0])
    c.line(x_inner[-1], y_inner[-1], x_outer[-1], y_outer[-1])
    # c.setDash([])  # Reset

  #  # Proper dotted guide arc for Front Width (Curved)
  #   guide_inner_r = inner_r + 10  # radial offset
  #   x_inner_guide = [center_x + guide_inner_r * cos(t) for t in theta_vals]
  #   y_inner_guide = [center_y + guide_inner_r * sin(t) for t in theta_vals]

  #   c.setStrokeColor(green)
  #   c.setDash(2, 2)
  #   for i in range(segments - 1):
  #       c.line(x_inner_guide[i], y_inner_guide[i], x_inner_guide[i+1], y_inner_guide[i+1])
  #   c.setDash([])
  #   # Proper dotted guide arc for Back Width (Curved)
  #   guide_outer_r = outer_r + 10  # radial offset
  #   x_outer_guide = [center_x + guide_outer_r * cos(t) for t in theta_vals]
  #   y_outer_guide = [center_y + guide_outer_r * sin(t) for t in theta_vals]

  #   c.setStrokeColor(green)
  #   c.setDash(2, 2)
  #   for i in range(segments - 1):
  #       c.line(x_outer_guide[i], y_outer_guide[i], x_outer_guide[i+1], y_outer_guide[i+1])



    c.setDash([])  # Reset dash
    #     # Label following Front Width (Curved) guide arc
    # label_index_inner = segments // 3
    # angle_inner = theta_vals[label_index_inner]
    # label_x_inner = x_inner_guide[label_index_inner]
    # label_y_inner = y_inner_guide[label_index_inner]

    # c.saveState()
    # c.translate(label_x_inner, label_y_inner)
    # c.rotate(angle_inner * 180 / pi)
    # c.setFont("Helvetica", 10)
    # c.setFillColor(blue)
    # c.drawString(0, 0, "Front Width (Curved)")
    # c.restoreState()

    # Label following Back Width (Curved) guide arc
    # label_index_outer = segments // 2
    # angle_outer = theta_vals[label_index_outer]
    # label_x_outer = x_outer_guide[label_index_outer]
    # label_y_outer = y_outer_guide[label_index_outer]

    # c.saveState()
    # c.translate(label_x_outer, label_y_outer)
    # c.rotate(angle_outer * 180 / pi)
    # c.setFont("Helvetica", 10)
    # c.setFillColor(green)
    # c.drawString(0, 0, "Back Width (Curved)")
    # c.restoreState()


    # Draw connecting sides
    c.setStrokeColor(black)
    # c.setDash([])
    c.line(x_inner[0], y_inner[0], x_outer[0], y_outer[0])
    c.line(x_inner[-1], y_inner[-1], x_outer[-1], y_outer[-1])


    # Draw straight lines
    c.setStrokeColor(green)
    c.setDash(1, 2)
    c.line(x_inner[0], y_inner[0], x_inner[-1], y_inner[-1])
    # c.setFont("Helvetica", 10)
    # c.setFillColor(blue)
    # c.drawCentredString((x_inner[0] + x_inner[-1])/2, (y_inner[0] + y_inner[-1])/2 - 12, "Front Width (Straight)")

    c.setStrokeColor(green)
    c.line(x_outer[0], y_outer[0], x_outer[-1], y_outer[-1])
    # c.setFont("Helvetica", 10)
    # c.setFillColor(green)
    # c.drawCentredString((x_outer[0] + x_outer[-1])/2, (y_outer[0] + y_outer[-1])/2 + 12, "Back Width (Straight)")

    # Length
    mid = segments // 2
    right_idx = -1
    label_x = x_outer[right_idx] + 20
    label_y = (y_outer[right_idx] + y_inner[right_idx]) / 2
    c.setStrokeColor(black)
    # c.setFont("Helvetica", 10)
    # c.setFillColor(black)
    # c.drawCentredString(label_x - 40, label_y, "Length")

    c.setFont("Helvetica", 10)
    c.setFillColor(black)
    c.drawRightString(center_x - outer_r + 10 , center_y, f"Thickness = {thickness}\"")

    # --- Draw piping around full cushion with dotted line ---
    piping_offset = 6  # outward/inward from cushion edges

    # Offset arcs
    x_piping_inner = [center_x + (inner_r - piping_offset) * cos(t) for t in theta_vals]
    y_piping_inner = [center_y + (inner_r - piping_offset) * sin(t) for t in theta_vals]
    x_piping_outer = [center_x + (outer_r + piping_offset) * cos(t) for t in theta_vals]
    y_piping_outer = [center_y + (outer_r + piping_offset) * sin(t) for t in theta_vals]

    # Set dotted line style
    c.setStrokeColor(blue)
    c.setDash(2, 2)

    # Draw inner arc (front curve)
    for i in range(segments - 1):

        c.line(x_piping_inner[i], y_piping_inner[i], x_piping_inner[i+1], y_piping_inner[i+1])

    # Right side (connect end of inner to end of outer)
    c.line(x_piping_inner[-1]-2, y_piping_inner[-1] - 2, x_piping_outer[-1]-3, y_piping_outer[-1] - 2)

    # Draw outer arc (back curve)
    for i in reversed(range(1, segments)):
        c.line(x_piping_outer[i], y_piping_outer[i], x_piping_outer[i-1], y_piping_outer[i-1])

    # Left side (connect start of outer to start of inner)
    c.line(x_piping_outer[0]-3, y_piping_outer[0]-3, x_piping_inner[0]-2, y_piping_inner[0]-3)

    # Reset dash
    # c.setDash([])

    # --- Arrow and label for "Piping" ---
    arrow_x_start = x_piping_outer[segments // 2] + 25
    arrow_y_start = y_piping_outer[segments // 2] + 25
    arrow_x_end = x_piping_outer[segments // 2]
    arrow_y_end = y_piping_outer[segments // 2]

    c.setStrokeColor(blue)
    c.line(arrow_x_start, arrow_y_start, arrow_x_end, arrow_y_end)
    c.setFont("Helvetica", 10)
    c.setFillColor(blue)
    c.drawString(arrow_x_start + 5, arrow_y_start + 5, "Piping")

    # --- Zipper Drawing (Conditional) ---
    zipper_color = red
    c.setStrokeColor(zipper_color)
    c.setFillColor(zipper_color)
    # c.setDash(1, 2)  # Dashed red line for zipper

    # Offset to prevent overlapping with cushion outline
    arc_zipper_offset = 8
    line_zipper_offset = 10

    if zipper_position.lower() == "long side" :
        # Zipper along entire back curve (outer arc) with offset
        x_zipper_arc = [center_x + (outer_r + arc_zipper_offset) * cos(t) for t in theta_vals]
        y_zipper_arc = [center_y + (outer_r + arc_zipper_offset) * sin(t) for t in theta_vals]

        for i in range(segments - 1):
            c.line(x_zipper_arc[i]+10, y_zipper_arc[i]+10, x_zipper_arc[i + 1]+10, y_zipper_arc[i + 1]+10)

        # Label at middle of arc
        mid_idx = segments // 2
        label_x = x_zipper_arc[mid_idx]
        label_y = y_zipper_arc[mid_idx] + 10
        c.setFont("Helvetica", 10)
        c.drawString(label_x + 20, label_y - 15, "Zipper")

    if zipper_position.lower() == "short side" :
        # Zipper on vertical short edge (right side), offset rightward
        zip_x1 = x_outer[-1] + line_zipper_offset
        zip_y1 = y_outer[-1]
        zip_x2 = x_inner[-1] + line_zipper_offset
        zip_y2 = y_inner[-1]

        c.line(zip_x1 - 15, zip_y1, zip_x2 - 15, zip_y2)



        # Label for side zipper
        label_x = zip_x2 + 5
        label_y = (zip_y1 + zip_y2) / 2 + 5
        c.setFont("Helvetica", 10)
        c.drawString(label_x - line_zipper_offset - 20, label_y+ 15, "Zipper")







    c.showPage()
# from reportlab.pdfgen import canvas

# # Define cushion data
# cushion_data = {
#     # "cushion_name": "Curved Cushion",
#     # "inner_radius": 3,
#     # "outer_radius": 10,
#     # "thickness": 2.5,
#     "piping": "Yes",
#     "quantity": 1,
#     # "zipper": "long side",
#     # "ties": "2 Curve Edge Ties"
#     "length": 20,
#     "back_width_curved": 138.75,
#     "back_width_straight": 129,
#     "front_width_curved": 118,
#     "front_width_straight": 111,
#     "thickness": 2,
#     "fill": "High Density Foam",
#     "fabric_collection": "Indoor Fabrics - Best Sellers",
#     "fabric_option": "New Royal Sr No 3 Shade 5",
#     "zipper": "long side"
# }

# pdf_filename = "test_output.pdf"
# c = canvas.Canvas(pdf_filename, pagesize=letter)
#     # Call the function directly
# draw_curved_cushion(c,cushion_data)

# c.save() # Add this line to save the PDF

#  # Force download link for Colab
# try:
#     from google.colab import files
#     files.download(pdf_filename)
# except ImportError:
#     print(f"Saved as {pdf_filename}. Not in Colab, manual download required.")


