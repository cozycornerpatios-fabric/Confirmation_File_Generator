from flask import Flask, request, jsonify, send_from_directory, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue, green
import os
import uuid
import sys

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        data = request.get_json(force=True)

        customer_name = data['customer_name']
        order_id = data['order_id']
        email = data['email']
        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        cushions = data['cushions']

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
            length_in = cushion['length']
            width_in = cushion['width']
            thickness = cushion['thickness']
            fill = cushion['fill']
            fabric = cushion['fabric']
            zipper_on = cushion['zipper']
            piping = cushion['piping']
            ties = cushion['ties']
            quantity = cushion['quantity']

            is_zipper_on_long = zipper_on == "Long Side"
            horizontal_side_in = max(length_in, width_in) if is_zipper_on_long else min(length_in, width_in)
            vertical_side_in = min(length_in, width_in) if is_zipper_on_long else max(length_in, width_in)

            left_x = 1 * inch
            y = page_height - 1 * inch
            c.setFont("Helvetica-Bold", 14)
            c.drawString(left_x, y, f"Cushion Specifications (Quantity: {quantity})")
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

            x_origin = (page_width - horizontal_side) / 2
            y_origin = 1.2 * inch
            piping_margin = 0.1 * inch if piping.lower() == "yes" else 0

            c.setStrokeColor(black)
            c.setLineWidth(1)
            c.rect(x_origin, y_origin, horizontal_side, vertical_side)

            # Draw thickness label to the left of the diagram
            c.setFont("Helvetica", 10)
            c.setFillColor(black)
            c.drawRightString(x_origin - 0.15 * inch, y_origin + vertical_side / 2, f"thickness = {thickness}\"")


            if piping.lower() == "yes":
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
                c.line(x_origin + horizontal_side + piping_margin, y_origin + vertical_side, label_x - 4, label_y + 4)

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
            tie_offset_in = 4
            tie_offset = tie_offset_in * scale_factor

            def draw_tie(x, y, direction, orientation='horizontal'):
                if orientation == 'horizontal':
                    if direction == 'left':
                        c.line(x, y, x - tie_len, y - tie_len)
                        c.line(x, y, x - tie_len, y + tie_len)
                    elif direction == 'right':
                        c.line(x, y, x + tie_len, y - tie_len)
                        c.line(x, y, x + tie_len, y + tie_len)
                elif orientation == 'vertical':
                    if direction == 'down':
                        c.line(x, y, x - tie_len, y - tie_len)
                        c.line(x, y, x + tie_len, y - tie_len)
                    elif direction == 'up':
                        c.line(x, y, x - tie_len, y + tie_len)
                        c.line(x, y, x + tie_len, y + tie_len)

            if ties.lower() != "none":
                short_side_is_vertical = vertical_side < horizontal_side
                xo = x_origin - piping_margin
                yo = y_origin - piping_margin
                hs = horizontal_side + 2 * piping_margin
                vs = vertical_side + 2 * piping_margin

                if ties == "2 Side Short" or ties=="2 Side":
                    if short_side_is_vertical:
                        mid_y = yo + vs / 2
                        draw_tie(xo, mid_y, 'left', 'horizontal')
                        draw_tie(xo + hs, mid_y, 'right', 'horizontal')
                    else:
                        mid_x = xo + hs / 2
                        draw_tie(mid_x, yo, 'down', 'vertical')
                        draw_tie(mid_x, yo + vs, 'up', 'vertical')

                elif ties == "2 Side Long":
                    if short_side_is_vertical:
                        mid_x = xo + hs / 2
                        draw_tie(mid_x, yo, 'down', 'vertical')
                        draw_tie(mid_x, yo + vs, 'up', 'vertical')
                    else:
                        mid_y = yo + vs / 2
                        draw_tie(xo, mid_y, 'left', 'horizontal')
                        draw_tie(xo + hs, mid_y, 'right', 'horizontal')

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

                elif ties == "4 Corner":
                    draw_tie(xo, yo, 'left', 'horizontal')
                    draw_tie(xo, yo + vs, 'left', 'horizontal')
                    draw_tie(xo + hs, yo, 'right', 'horizontal')
                    draw_tie(xo + hs, yo + vs, 'right', 'horizontal')

                elif ties == "2 Backside":
                    draw_tie(x_origin + horizontal_side / 2 - 0.4 * inch - 6, y_origin + vertical_side / 2, 'down', 'vertical')
                    draw_tie(x_origin + horizontal_side / 2 + 0.4 * inch + 6, y_origin + vertical_side / 2, 'down', 'vertical')

            c.showPage()

        c.save()
        return jsonify({"pdf_link": url_for('serve_pdf', filename=filename, _external=True)})

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

from flask import render_template_string

@app.route('/')
def index():
    return render_template_string(open("form.html").read())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)



