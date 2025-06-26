from flask import Flask, request, jsonify, send_from_directory, render_template_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, purple, green
import math
import os
import uuid

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template_string(open("Index.html").read())

@app.route('/generate-trapezoid', methods=['POST'])
def generate_trapezoid():
    try:
        data = request.get_json(force=True)

        cushions = data['cushions']
        customer_name = data['customer_name']
        order_number = data['order_number']
        email = data['email']
        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        location = data['location']
        delivery_method = data['delivery_method']

        filename = f"trapezoid_diagram_{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(PDF_DIR, filename)
        c = canvas.Canvas(output_path, pagesize=letter)

        # Page 1: Customer Details
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 740, "Customer Order Information")
        c.setFont("Helvetica", 12)
        c.drawString(100, 710, f"Customer Name: {customer_name}")
        c.drawString(100, 690, f"Order Number: {order_number}")
        c.drawString(100, 670, f"Email: {email}")
        c.drawString(100, 650, f"Shipping Address: {shipping_address}")
        c.drawString(100, 630, f"Billing Address: {billing_address}")
        c.drawString(100, 610, f"Location: {location}")
        c.drawString(100, 590, f"Delivery Method: {delivery_method}")
        c.showPage()

        for cushion in cushions:
            top_base_in = cushion['top_base']
            bottom_base_in = cushion['bottom_base']
            height_in = cushion['height']
            zipper_position = cushion['zipper']
            piping = cushion['piping']
            ties_option = cushion['ties']
            product_details = cushion['product_details']

            c.setFont("Helvetica-Bold", 14)
            c.drawString(100, 740, f"Tie Option: {ties_option}")
            y = 715
            c.setFont("Helvetica", 12)
            for line in product_details:
                c.drawString(100, y, line)
                y -= 18

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

            def draw_ties(opt):
                if opt == "2 Back Ties":
                    center_y = (i_tl[1] + i_bl[1]) / 2
                    center_x_left = (i_bl[0] + i_br[0]) / 2 - 40
                    center_x_right = (i_bl[0] + i_br[0]) / 2 + 40
                    draw_tie(center_x_left, center_y, "down")
                    draw_tie(center_x_right, center_y, "down")
                elif opt == "2 Corner Ties":
                    draw_tie(bottom_left[0], bottom_left[1], 'left')
                    draw_tie(bottom_right[0], bottom_right[1], 'right')
                elif opt == "2 Side Ties":
                    draw_tie(mid_left[0], mid_left[1], 'left')
                    draw_tie(mid_right[0], mid_right[1], 'right')
                elif opt == "4 Corner Ties":
                    draw_tie(top_left[0], top_left[1], 'left')
                    draw_tie(top_right[0], top_right[1], 'right')
                    draw_tie(bottom_left[0], bottom_left[1], 'left')
                    draw_tie(bottom_right[0], bottom_right[1], 'right')

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
            c.showPage()

        c.save()
        return jsonify({"pdf_link": f"/pdfs/{filename}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
