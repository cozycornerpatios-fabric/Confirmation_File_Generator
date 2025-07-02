import os
import uuid
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, purple, green
from google.colab import files



# === INPUT DATA ===
# cushions = [
#     {
#         "top_base": 114,
#         "bottom_base": 59,
#         "height": 26,
#         "zipper": "Long Side",  # Short Side, Long Side, Angled Side, ShortPlusAngled
#         "piping": "No" , # Yes or No
#         "ties": "4 Corner Ties", # No Ties, 2 Side Ties, 2 Back Ties, 2 Corner Ties, 4 Corner Ties,2 Top Ties
#          "cushion_name": "Trapezoid Bay Window Cushions",
#           "quantity" :1,
#         "thickness": 2,
#         "tie_offset_from_base": 3,  # Default or custom as needed
#         "product_details": [
#             "Product: Trapezoid Bay Window Cushions",
#             "Design ID: (D#8Q1IA1U)",
#             "SKU: Trp-win-cus",
#             "Length (inches): 26",
#             "Bottom Width (inches): 59",
#             "Top Width (inches): 114",
#             "Thickness (inches): 2",
#             "Fill: Covers Only",
#             "Fabrics Collections: Indoor Fabrics - Best Sellers",
#             "Fabric Options: LIZZO CHERRO-LYRA-IVORY Sr. No 17",
#             "Piping: Yes",
#             "Ties: 2 Back Ties",


#         ]
#     }
# ]


# customer_name = "John Doe"
# order_number = "ORD-12345"
# email = "john@example.com"
# shipping_address = "123 Street, City, State, ZIP"
# billing_address = "456 Avenue, City, State, ZIP"
# location = "1499 W 120th Ave"
# delivery_method = "Standard Shipping"

# # === OUTPUT FILE SETUP ===
# PDF_DIR = "/mnt/data/pdfs"
# os.makedirs(PDF_DIR, exist_ok=True)
# filename = f"trapezoid_diagram_{uuid.uuid4().hex}.pdf"
# output_path = os.path.join(PDF_DIR, filename)
# c = canvas.Canvas(output_path, pagesize=letter)

# # === PAGE 1: CUSTOMER INFO ===
# c.setFont("Helvetica-Bold", 14)
# c.drawString(100, 740, "Customer Order Information")
# c.setFont("Helvetica", 12)
# c.drawString(100, 710, f"Customer Name: {customer_name}")
# c.drawString(100, 690, f"Order Number: {order_number}")
# c.drawString(100, 670, f"Email: {email}")
# c.drawString(100, 650, f"Shipping Address: {shipping_address}")
# c.drawString(100, 630, f"Billing Address: {billing_address}")
# c.drawString(100, 610, f"Location: {location}")
# c.drawString(100, 590, f"Delivery Method: {delivery_method}")
# c.showPage()

# === DRAW PAGES FOR EACH CUSHION ===
def draw_trapezium(c,cushion):
    page_width, page_height = letter
    cushion_name = cushion.get('cushion_name', 'Cushion Specifications')
    top_base_in = cushion['top_base']
    bottom_base_in = cushion['bottom_base']
    if(top_base_in > bottom_base_in):
        top_base_in, bottom_base_in = bottom_base_in, top_base_in
    height_in = cushion['height']
    zipper_position = cushion['zipper']
    piping = cushion['piping']
    ties_option = cushion['ties']
    tie_offset = cushion.get("tie_offset_from_base", 0)
    thickness_in = cushion.get('thickness', None)
    quantity = cushion.get('quantity', 1)

    # c.setFont("Helvetica-Bold", 14)
    # c.drawString(100, 740, f"Tie Option: {ties_option}")
    # c.setFont("Helvetica", 12)
    # y = 715
    # for line in product_details:
    #  ,   c.drawString(100, y, line)
    #     y -= 18
    left_x = 1 * inch
    y = page_height - 1 * inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_x, y, f"{cushion_name} (Quantity: {quantity})")
    
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

    # Define printable area (letter page = 8.5 x 11 inches)
    
    margin = 0.75 * inch
    usable_width = page_width - 2 * margin
    usable_height = page_height - 2 * margin

   # === NEW DIAGRAM SCALING AND POSITIONING ===

    margin = 0.75 * inch
    usable_width = page_width - 2 * margin

    # The y position where the text ends is already tracked in `y`
    # The remaining vertical space is from margin (bottom) to y
    diagram_usable_height = y - margin

    # Compute physical dimensions
    max_physical_width = max(top_base_in, bottom_base_in)
    max_physical_height = height_in

    # Compute scale to fit both width and height
    scale_x = usable_width / max_physical_width
    scale_y = diagram_usable_height / max_physical_height
    scale = min(scale_x, scale_y)

    # Recalculate dimensions
    top_base = top_base_in * scale
    bottom_base = bottom_base_in * scale
    height = height_in * scale

    # Center horizontally
    x_origin = (page_width - bottom_base) / 2

    # Diagram starts at bottom margin
    y_origin = margin


    

    top_left = (x_origin + (bottom_base - top_base) / 2, y_origin + height)
    top_right = (top_left[0] + top_base, top_left[1])
    bottom_left = (x_origin, y_origin)
    bottom_right = (x_origin + bottom_base, y_origin)
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

    # Tie anchors based on piping
    tie_top_left = top_left if piping == "Yes" else i_tl
    tie_top_right = top_right if piping == "Yes" else i_tr
    tie_bottom_left = bottom_left if piping == "Yes" else i_bl
    tie_bottom_right = bottom_right if piping == "Yes" else i_br


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
        c.line(x_ref, y_ref, x_tie, y_tie)
        c.setDash()

    def draw_short_side_ties():
        tie_offset_top = tie_offset * scale  # scale the offset

        # LEFT TIE — attach to correct anchor
        x_left_tie = tie_top_left[0] + tie_offset_top
        y_left_tie = tie_top_left[1]
        draw_tie(x_left_tie, y_left_tie, "up")

        # RIGHT TIE — attach to correct anchor
        x_right_tie = tie_top_right[0] - tie_offset_top
        y_right_tie = tie_top_right[1]
        draw_tie(x_right_tie, y_right_tie, "up")

    def draw_ties(opt):
        if opt == "2 Side Ties":
            dx_left = tie_top_left[0] - tie_bottom_left[0]
            dy_left = tie_top_left[1] - tie_bottom_left[1]
            ratio_left = min(1, tie_offset / slant_len_in)
            x_left = tie_bottom_left[0] + dx_left * ratio_left
            y_left = tie_bottom_left[1] + dy_left * ratio_left
            draw_tie(x_left, y_left, "left")

            dx_right = tie_top_right[0] - tie_bottom_right[0]
            dy_right = tie_top_right[1] - tie_bottom_right[1]
            ratio_right = min(1, tie_offset / slant_len_in)
            x_right = tie_bottom_right[0] + dx_right * ratio_right
            y_right = tie_bottom_right[1] + dy_right * ratio_right
            draw_tie(x_right, y_right, "right")

        elif opt == "4 Corner Ties":
            draw_tie(tie_bottom_left[0], tie_bottom_left[1], "down")
            draw_tie(tie_bottom_right[0], tie_bottom_right[1], "down")
            draw_tie(tie_top_left[0], tie_top_left[1], "up")
            draw_tie(tie_top_right[0], tie_top_right[1], "up")

        elif opt == "2 Corner Ties":
            draw_tie(tie_bottom_left[0], tie_bottom_left[1], "down")
            draw_tie(tie_bottom_right[0], tie_bottom_right[1], "down")

        elif opt == "2 Back Ties":
            left_x = tie_bottom_left[0] + (tie_bottom_right[0] - tie_bottom_left[0]) * (tie_offset / bottom_base_in)
            right_x = tie_bottom_right[0] - (tie_bottom_right[0] - tie_bottom_left[0]) * (tie_offset / bottom_base_in)
            y = tie_bottom_left[1]
            draw_tie(left_x, y, "down")
            draw_tie(right_x, y, "down")
        elif opt == "2 Top Ties":
            draw_short_side_ties()

    # Draw shapes
    if piping == "Yes":
        c.setStrokeColor(purple)
        c.setLineWidth(1.6)
        c.lines([
            (top_left[0], top_left[1], top_right[0], top_right[1]),
            (top_right[0], top_right[1], bottom_right[0], bottom_right[1]),
            (bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1]),
            (bottom_left[0], bottom_left[1], top_left[0], top_left[1])
        ])

    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.lines([
        (i_tl[0], i_tl[1], i_tr[0], i_tr[1]),
        (i_tr[0], i_tr[1], i_br[0], i_br[1]),
        (i_br[0], i_br[1], i_bl[0], i_bl[1]),
        (i_bl[0], i_bl[1], i_tl[0], i_tl[1])
    ])

    # Draw zipper (unchanged logic)
    c.setStrokeColor(red)
    c.setLineWidth(1.5)
    c.setFillColor(red)
    c.setFont("Helvetica-Bold", 12)
    dynamic_offset = min(bottom_base, height) * 0.03
    if zipper_position == "Short Side":
        c.line(top_left[0], top_left[1] + dynamic_offset, top_right[0], top_right[1] + dynamic_offset)
        c.drawCentredString((top_left[0] + top_right[0]) / 2, top_left[1] + dynamic_offset, "Zipper")
    elif zipper_position == "Long Side":
        c.line(bottom_left[0], bottom_left[1] - dynamic_offset, bottom_right[0], bottom_right[1] - dynamic_offset)
        c.drawCentredString((bottom_left[0] + bottom_right[0]) / 2, bottom_left[1] - dynamic_offset - 11, "Zipper")
    elif zipper_position == "Angled Side":
        # c.line(bottom_left[0] - dynamic_offset, bottom_left[1], top_left[0] - dynamic_offset, top_left[1])
        # c.drawString(bottom_left[0] - dynamic_offset, (top_left[1] + bottom_left[1]) / 2 + dynamic_offset, "Zipper")

        c.line(bottom_right[0] + dynamic_offset, bottom_right[1], top_right[0] + dynamic_offset, top_right[1])
        c.drawString(bottom_right[0]-50, (top_right[1] + bottom_right[1]) / 2, "Zipper")
    elif zipper_position == "ShortPlusAngled":

        c.line(top_left[0], top_left[1] + dynamic_offset, top_right[0], top_right[1] + dynamic_offset)
        c.drawCentredString((top_left[0] + top_right[0]) / 2, top_left[1] + dynamic_offset + 5, "Zipper")

        c.line((bottom_left[0] + top_left[0])/2 - dynamic_offset, (bottom_left[1]+top_left[1])/2, top_left[0] - dynamic_offset, top_left[1])

        c.line((bottom_right[0] + top_right[0])/2 + 10 - dynamic_offset, (bottom_right[1]+top_right[1])/2, top_right[0] + dynamic_offset, top_right[1])
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

    # Calculate midpoints of the slanted sides for dimension labels
    mid_left = ((i_bl[0] + i_tl[0]) / 2, (i_bl[1] + i_tl[1]) / 2)
    mid_right = ((i_br[0] + i_tr[0]) / 2, (i_br[1] + i_tr[1]) / 2)

    c.drawString(mid_left[0] + 10, mid_left[1] - 5, f'{slant_len_in}"')
    c.drawString(mid_right[0] - 40, mid_right[1] - 5, f'{slant_len_in}"')

    thickness_in = cushion.get('thickness', None)
    c.drawCentredString(
        i_bl[0] - 100,

        (i_tl[1] + i_bl[1]) / 2 - 10,
        f"Thickness: {thickness_in}\""
    )

    c.showPage()

