from flask import Flask, request, jsonify, send_from_directory, url_for, render_template_string
from reportlab.lib.pagesizes import letter
import os
import uuid

# Import drawers
from rectangle_drawer import draw_rectangle
from trapezium_drawer import draw_trapezium
from L_shaped_drawer import draw_l_shape
from clipped_trapeze_drawer import draw_clipped_trapeze
from T_shaped_drawer import draw_t_shape
from round_drawer import draw_round
from E_triangle_drawer import draw_equilateral_triangle
from curved_drawer import draw_curved
from semi_round_drawer import draw_semi_round
from right_triangle_drawer import draw_right_triangle
from Curved_indoor_Cushions_drawer import draw_curved_cushion
from right_cushion_drawer import draw_right_cushion
from tapered_bolster_drawer import draw_tapered_bolster
from left_cushion_drawer import draw_left_cushion
from counter_utils import increment_counter

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        print(f"Received request to /generate-confirmation")
        api_call_number = increment_counter()
        print(f"API call count: {api_call_number}")

        data = request.get_json(force=True)
        print(f"Request data received: {data}")

        # ✅ Support single order (dict) OR multiple orders (list of dicts)
        if isinstance(data, dict):
            orders = [data]
        elif isinstance(data, list):
            orders = data
        else:
            raise ValueError("Invalid payload format. Must be dict or list of dicts.")

        for order in orders:
            customer_name = order['customer_name']
            order_id = order['order_id']
            email = order['email']
            shipping_address = order['shipping_address']
            billing_address = order['billing_address']
            cushions = order['cushions']

            filename = f"confirmation_{order_id}_{uuid.uuid4().hex}.pdf"
            filepath = os.path.join(PDF_DIR, filename)

            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            c = canvas.Canvas(filepath, pagesize=letter)
            page_width, page_height = letter

            # -------------------------------
            # PAGE 1 - CUSTOMER INFO
            # -------------------------------
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

            # -------------------------------
            # PAGES 2+ - CUSHIONS
            # -------------------------------
            print(f"Processing {len(cushions)} cushions for order {order_id}...")
            for i, cushion in enumerate(cushions):
                print(f"Processing cushion {i+1}: {cushion.get('cushion_name', 'Unnamed')}")

                # 🔎 Shape detection & drawing
                if all(cushion.get(k, 0) > 0 for k in ("length", "top_width", "bottom_width", "ear", "thickness")):
                    if cushion.get("top_width") > cushion.get("bottom_width"):
                        draw_t_shape(c, cushion)
                    else:
                        draw_l_shape(c, cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("diameter", "thickness")):
                    name = cushion.get("cushion_name", "").lower()
                    if "semi" in name:
                        draw_semi_round(c, cushion)
                    else:
                        draw_round(c, cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("front_width_straight", "back_width_straight","thickness","front_width_curved","back_width_curved")):
                    draw_curved_cushion(c,cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("top_thickness", "bottom_thickness","height","length")):
                    draw_tapered_bolster(c,cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("width", "side_length","middle_length")):
                    draw_curved(c,cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("side", "thickness")):
                    draw_equilateral_triangle(c, cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "length")):
                    name = cushion.get("cushion_name", "").lower()
                    if "left" in name:
                        draw_left_cushion(c, cushion)
                    else: 
                        draw_right_cushion(c,cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "height","edge")):
                    draw_clipped_trapeze(c,cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("top_base", "bottom_base", "height")):
                    draw_trapezium(c, cushion)
                elif all(cushion.get(k, 0) > 0 for k in ("width", "length", "thickness")):
                    name = cushion.get("cushion_name", "").lower()
                    if "triangle" in name:
                        draw_right_triangle(c, cushion)
                    else: 
                        draw_rectangle(c, cushion)
                else:
                    raise ValueError("Unable to determine cushion shape. Missing key dimensions.")

            c.save()
            print(f"✅ PDF generated for order {order_id}: {filepath}")

        # ✅ Instead of returning links, just confirm generation
        return "PDF(s) generated successfully and saved in /pdfs folder."

    except Exception as e:
        import sys
        print("ERROR:", e, file=sys.stderr)
        return f"Error: {str(e)}", 500


@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

@app.route('/')
def index():
    return render_template_string(open("form.html").read())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
