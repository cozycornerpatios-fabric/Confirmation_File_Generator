from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue, green
import os
import uuid
from IPython.display import FileLink, display
from google.colab import files

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def generate_confirmation(customer_name, order_id, email, shipping_address, billing_address, cushions):
    filename = f"confirmation_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    page_width, page_height = letter

    # Customer details page
    c.setFont("Helvetica-Bold", 20)
    c.drawString(1 * inch, page_height - 1 * inch, "ORDER CONFIRMATION")
    y_left = page_height - 1.6 * inch
    details = [
        ("Customer Name", customer_name),
        ("Order Number", order_id),
        ("Email", email),
        ("Shipping Address", "")
    ] + [("", line) for line in shipping_address] + [
        ("Billing Address", "")
    ] + [("", line) for line in billing_address]

    for label, value in details:
        if label:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, y_left, f"{label}:")
            c.setFont("Helvetica", 12)
            c.drawString(2.8 * inch, y_left, value)
        elif value:
            c.setFont("Helvetica", 12)
            c.drawString(1.2 * inch, y_left, value)
        y_left -= 0.25 * inch
    c.showPage()

    for cushion in cushions:
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

        if 'tie_offset_from_corner' in cushion:
            tie_offset_from_corner = cushion['tie_offset_from_corner']
            if not isinstance(tie_offset_from_corner, (int, float)) or tie_offset_from_corner < 0:
                # return jsonify({"error": f"Invalid tie_offset_from_corner: must be a non-negative number."}), 400
                print(f"Error: Invalid tie_offset_from_corner: must be a non-negative number.")
                return
            if tie_offset_from_corner >= short_side_length / 2:
                # return jsonify({"error": f"tie_offset_from_corner too large: must be less than half of the short side length ({short_side_length / 2} inches)."}), 400
                print(f"Error: tie_offset_from_corner too large: must be less than half of the short side length ({short_side_length / 2} inches).")
                return
        else:
            if ties in ["2 Side", "2 Side Short", "2 Side Long"]:
                tie_offset_from_corner = short_side_length / 2
            elif ties.startswith("4 Side"):
                tie_offset_from_corner = min(short_side_length * 0.2, 4)  # 20% or 4 inches max
            else:
                tie_offset_from_corner = 4  # fallback default






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
        c.drawRightString(x_origin - 0.15 * inch - 20, y_origin + vertical_side / 2, f"thickness = {thickness}\"")


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
                elif direction == 'right':
                    c.line(x, y, x + tie_len, y - tie_len)
                    c.line(x, y, x + tie_len, y + tie_len)
                    label_x = x + tie_len + 2
                    label_y = y
            elif orientation == 'vertical':
                if direction == 'down':
                    c.line(x, y, x - tie_len, y - tie_len)
                    c.line(x, y, x + tie_len, y - tie_len)
                    label_x = x
                    label_y = y - tie_len - 8
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

            if ties == "2 Side Short" or ties=="2 Side":
                if short_side_is_vertical:
                    draw_tie(xo,  yo + tie_offset, 'left', 'horizontal')
                    draw_tie(xo + hs,  yo + tie_offset, 'right', 'horizontal')
                else:
                    draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')

                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")


            elif ties == "2 Side Long":
                if short_side_is_vertical:
                    draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                else:
                    draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                    draw_tie(xo + hs, yo + tie_offset, 'right', 'horizontal')

                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")

            elif ties == "4 Side Short" or ties=="4 Side":
                if short_side_is_vertical:
                    draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                    draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                    draw_tie(xo + hs, yo + tie_offset, 'right', 'horizontal')
                    draw_tie(xo + hs, yo + vs - tie_offset, 'right', 'horizontal')
                else:
                    draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + hs - tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                    draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')

                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")

            elif ties == "4 Side Long":
                if short_side_is_vertical:
                    draw_tie(xo + tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + hs - tie_offset, yo, 'down', 'vertical')
                    draw_tie(xo + tie_offset, yo + vs, 'up', 'vertical')
                    draw_tie(xo + hs - tie_offset, yo + vs, 'up', 'vertical')
                else:
                    draw_tie(xo, yo + tie_offset, 'left', 'horizontal')
                    draw_tie(xo, yo + vs - tie_offset, 'left', 'horizontal')
                    draw_tie(xo + hs, yo + tie_offset, 'right', 'horizontal')
                    draw_tie(xo + hs, yo + vs - tie_offset, 'right', 'horizontal')

                c.setFont("Helvetica", 8)
                c.setFillColor(green)
                c.drawString(label_x, label_y, f"Tie ({tie_offset_from_corner}\")")

            elif ties == "4 Corner":
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
                c.drawString(x_origin + width_offset_scaled + 2, y_origin + length_offset_scaled - 10, f"{tie_offset_width}\"")
                c.drawString(x_origin + horizontal_side - width_offset_scaled + 2, y_origin + length_offset_scaled - 10, f"{tie_offset_width}\"")
                c.drawString(x_origin + horizontal_side / 2 - 20, y_origin + length_offset_scaled + 10, f"{tie_offset_length}\"")


        c.showPage()

    c.save()
    print(f"PDF generated: {filepath}")
    files.download(filepath)
    display(FileLink(filepath))

# Example usage (replace with real values)
generate_confirmation(
    customer_name="John Doe",
    order_id="12345",
    email="john@example.com",
    shipping_address=["123 Main St", "City, Country"],
    billing_address=["456 Billing Rd", "City, Country"],
    cushions=[
        {
            "cushion_name": "Seat Cushion A",
            "length": 20,
            "width": 18,
            "thickness": 4,
            "fill": "Foam",
            "fabric": "Blue Cotton",
            "zipper": "Short Side",
            "piping": "Yes",
            "ties": "2 Backside",
            "tie_offset_from_corner":7,
            "tie_offset_length": 9,
            "tie_offset_width": 6,
            "quantity": 1
        }
    ]
)
