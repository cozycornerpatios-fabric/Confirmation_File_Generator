from flask import Flask, request, jsonify, send_from_directory, render_template_string, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import black, red, purple, green, blue
import os
import uuid
import math

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template_string(open("form.html").read())

@app.route('/generate-cushions', methods=['POST'])
def generate_cushions():
    try:
        data = request.get_json(force=True)

        # Common order fields
        customer_name = data['customer_name']
        order_id = data.get('order_id', data.get('order_number'))
        email = data['email']
        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        location = data.get('location')
        delivery_method = data.get('delivery_method')
        cushions = data['cushions']

        # Prepare PDF
        filename = f"cushion_diagram_{uuid.uuid4().hex}.pdf"
        output_path = os.path.join(PDF_DIR, filename)
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter

        # Page 1: Order Info
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, "Order Information")
        c.setFont("Helvetica", 12)
        y = height - 1.4*inch
        c.drawString(1*inch, y, f"Customer Name: {customer_name}")
        y -= 0.25*inch
        c.drawString(1*inch, y, f"Order Number: {order_id}")
        y -= 0.25*inch
        c.drawString(1*inch, y, f"Email: {email}")
        y -= 0.25*inch

        # Shipping Address
        lines = shipping_address if isinstance(shipping_address, list) else [shipping_address]
        c.drawString(1*inch, y, "Shipping Address:")
        y -= 0.2*inch
        for line in lines:
            c.drawString(1.2*inch, y, line)
            y -= 0.2*inch

        # Billing Address
        y -= 0.1*inch
        lines = billing_address if isinstance(billing_address, list) else [billing_address]
        c.drawString(1*inch, y, "Billing Address:")
        y -= 0.2*inch
        for line in lines:
            c.drawString(1.2*inch, y, line)
            y -= 0.2*inch

        # Optional fields
        if location:
            y -= 0.1*inch
            c.drawString(1*inch, y, f"Location: {location}")
            y -= 0.25*inch
        if delivery_method:
            c.drawString(1*inch, y, f"Delivery Method: {delivery_method}")
            y -= 0.25*inch

        c.showPage()

        # Loop through cushions
        for cushion in cushions:
            cushion_name = cushion.get('cushion_name', 'Cushion')
            shape = 'trapezoid' if 'trapezoid' in cushion_name.lower() else 'rectangle'

            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, height - 1*inch, cushion_name)

            if shape == 'trapezoid':
                # Trapezoid-specific fields
                top_base_in = cushion['top_base']
                bottom_base_in = cushion['bottom_base']
                height_in = cushion['height']
                zipper_position = cushion['zipper']
                piping = cushion['piping']
                ties_option = cushion['ties']
                product_details = cushion.get('product_details', [])
                thickness_in = cushion.get('thickness')

                # Product details
                y_text = height - 1.4*inch
                c.setFont("Helvetica", 12)
                for line in product_details:
                    c.drawString(1*inch, y_text, line)
                    y_text -= 0.2*inch

                # Scale and draw trapezoid
                max_w = 5*inch
                max_h = 4*inch
                scale = min(max_w / bottom_base_in, max_h / height_in)
                top_b = top_base_in * scale
                bot_b = bottom_base_in * scale
                h = height_in * scale
                x0 = 1.5*inch
                y0 = 2.5*inch
                tl = (x0 + (bot_b - top_b)/2, y0 + h)
                tr = (tl[0] + top_b, tl[1])
                bl = (x0, y0)
                br = (x0 + bot_b, y0)
                slant_len = round(math.hypot((bottom_base_in - top_base_in)/2, height_in), 2)

                def inset_corner(pt, adj1, adj2, amt):
                    dx1, dy1 = adj1[0]-pt[0], adj1[1]-pt[1]
                    dx2, dy2 = adj2[0]-pt[0], adj2[1]-pt[1]
                    l1, l2 = math.hypot(dx1,dy1), math.hypot(dx2,dy2)
                    dx = dx1/l1 + dx2/l2
                    dy = dy1/l1 + dy2/l2
                    norm = math.hypot(dx,dy)
                    return (pt[0] + dx/norm*amt, pt[1] + dy/norm*amt)

                inset = 10
                i_tl = inset_corner(tl, tr, bl, inset)
                i_tr = inset_corner(tr, tl, br, inset)
                i_br = inset_corner(br, bl, tr, inset)
                i_bl = inset_corner(bl, br, tl, inset)

                # Piping border
                if piping.lower() == 'yes':
                    c.setStrokeColor(purple)
                    c.setLineWidth(1.6)
                    c.lines([
                        (tl[0], tl[1], tr[0], tr[1]),
                        (tr[0], tr[1], br[0], br[1]),
                        (br[0], br[1], bl[0], bl[1]),
                        (bl[0], bl[1], tl[0], tl[1])
                    ])
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(tr[0]+30, tr[1]-20, "Piping")

                # Main inset shape
                c.setStrokeColor(black)
                c.setLineWidth(1)
                c.lines([
                    (i_tl[0], i_tl[1], i_tr[0], i_tr[1]),
                    (i_tr[0], i_tr[1], i_br[0], i_br[1]),
                    (i_br[0], i_br[1], i_bl[0], i_bl[1]),
                    (i_bl[0], i_bl[1], i_tl[0], i_tl[1])
                ])

                # Zipper
                c.setStrokeColor(red)
                c.setLineWidth(1.5)
                c.setFillColor(red)
                c.setFont("Helvetica-Bold", 12)
                if zipper_position.lower() == 'top':
                    c.line(tl[0], tl[1]+10, tr[0], tr[1]+10)
                    c.drawCentredString((tl[0]+tr[0])/2, tl[1]+15, "Zipper")
                elif zipper_position.lower() == 'bottom':
                    c.line(bl[0], bl[1]-10, br[0], br[1]-10)
                    c.drawCentredString((bl[0]+br[0])/2, bl[1]-20, "Zipper")
                elif zipper_position.lower() == 'left':
                    c.line(bl[0]-10, bl[1], tl[0]-10, tl[1])
                    c.drawString(bl[0]-40, (tl[1]+bl[1])/2, "Zipper")
                elif zipper_position.lower() == 'right':
                    c.line(br[0]+10, br[1], tr[0]+10, tr[1])
                    c.drawString(br[0]+10, (tr[1]+br[1])/2, "Zipper")

                # Ties function
                def draw_tie(x, y, dir):
                    c.setStrokeColor(green)
                    c.setLineWidth(1)
                    length = 20
                    if dir == 'left':
                        c.line(x, y, x-length, y+length)
                        c.line(x, y, x-length, y-length)
                    elif dir == 'right':
                        c.line(x, y, x+length, y+length)
                        c.line(x, y, x+length, y-length)
                    elif dir == 'down':
                        c.line(x, y, x-length, y-length)
                        c.line(x, y, x+length, y-length)
                    c.setFont("Helvetica", 8)
                    c.drawString(x-5, y-5, "Tie")

                if ties_option.lower().startswith('2 back'):
                    mid_x = (bl[0]+br[0])/2
                    mid_y = (i_bl[1]+i_tl[1])/2
                    draw_tie(mid_x-40, mid_y, 'down')
                    draw_tie(mid_x+40, mid_y, 'down')
                elif ties_option.lower().startswith('2 corner'):
                    draw_tie(bl[0], bl[1], 'left')
                    draw_tie(br[0], br[1], 'right')
                elif ties_option.lower().startswith('2 side'):
                    mid_y = (i_bl[1]+i_tl[1])/2
                    draw_tie(i_bl[0], mid_y, 'left')
                    draw_tie(i_br[0], mid_y, 'right')
                elif ties_option.lower().startswith('4 corner'):
                    draw_tie(tl[0], tl[1], 'left')
                    draw_tie(tr[0], tr[1], 'right')
                    draw_tie(bl[0], bl[1], 'left')
                    draw_tie(br[0], br[1], 'right')

                # Dimension labels
                c.setFont("Helvetica", 10)
                c.setFillColor(black)
                # Top/base
                c.drawCentredString((i_tl[0]+i_tr[0])/2, i_tl[1]+5, f"{top_base_in}\"")
                c.drawCentredString((i_bl[0]+i_br[0])/2, i_bl[1]-15, f"{bottom_base_in}\"")
                # Height
                c.drawString(i_tr[0]+10, (i_tr[1]+i_br[1])/2, f"{height_in}\"")
                # Slant
                mid_l = ((tl[0]+bl[0])/2, (tl[1]+bl[1])/2)
                mid_r = ((tr[0]+br[0])/2, (tr[1]+br[1])/2)
                c.drawString(mid_l[0]+5, mid_l[1]-5, f"{slant_len}\"")
                c.drawString(mid_r[0]-40, mid_r[1]-5, f"{slant_len}\"")

                if thickness_in:
                    c.drawString(i_bl[0]-50, (i_bl[1]+i_tl[1])/2-10, f"Thickness: {thickness_in}\"")

            else:
                # Rectangle-specific fields
                length_in = cushion['length']
                width_in = cushion['width']
                thickness = cushion['thickness']
                fill = cushion['fill']
                fabric = cushion['fabric']
                zipper_on = cushion['zipper']
                piping = cushion['piping']
                ties = cushion['ties']
                quantity = cushion.get('quantity', 1)

                # Specs text
                y_text = height - 1.4*inch
                c.setFont("Helvetica", 12)
                specs = [
                    ("Quantity", quantity),
                    ("Length", f"{length_in} inches"),
                    ("Width", f"{width_in} inches"),
                    ("Thickness", f"{thickness} inches"),
                    ("Fill", fill),
                    ("Fabric", fabric),
                    ("Zipper Position", zipper_on),
                    ("Piping", piping),
                    ("Ties", ties)
                ]
                for label, val in specs:
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(1*inch, y_text, f"{label}:")
                    c.setFont("Helvetica", 12)
                    c.drawString(1*inch+120, y_text, str(val))
                    y_text -= 0.3*inch

                # Draw rectangle
                diag_w = width - 2*inch
                diag_h = height/3
                scale = min(diag_w/length_in, diag_h/width_in)
                h = length_in*scale if zipper_on.lower().startswith('long') else width_in*scale
                w = width_in*scale if zipper_on.lower().startswith('long') else length_in*scale
                x0 = (width-w)/2
                y0 = 1.2*inch
                # main rect
                c.setStrokeColor(black)
                c.setLineWidth(1)
                c.rect(x0, y0, w, h)
                # thickness label
                c.setFont("Helvetica", 10)
                c.drawRightString(x0-10, y0+h/2, f"thickness = {thickness}\"")
                # piping
                if piping.lower() == 'yes':
                    pm = 0.1*inch
                    c.setStrokeColor(blue)
                    c.rect(x0-pm, y0-pm, w+2*pm, h+2*pm)
                    c.drawString(x0+w+pm+5, y0+h+pm, "Piping")
                # zipper
                c.setStrokeColor(red)
                c.setLineWidth(2)
                zip_y = y0 + h + 0.1*inch
                c.line(x0, zip_y, x0+w, zip_y)
                c.drawCentredString(x0+w/2-20, zip_y+5, "Zipper")
                # ties
                c.setStrokeColor(green)
                c.setLineWidth(1.2)
                def tie(dx, dy):
                    l = 0.3*inch
                    c.line(dx, dy, dx-l, dy-l)
                    c.line(dx, dy, dx+l, dy-l)
                if ties.lower() != 'none':
                    # simple: put two ties center-bottom
                    tie(x0+w/2-12, y0)
                    tie(x0+w/2+12, y0)

            c.showPage()

        c.save()
        return jsonify({"pdf_link": url_for('serve_pdf', filename=filename, _external=True)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
