from flask import Flask, request, jsonify, send_from_directory, url_for, render_template_string
from reportlab.lib.pagesizes import letter
import os
import uuid
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
from counter_utils import increment_counter
from left_cushion_drawer import draw_left_cushion

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

def draw_cushion_by_shape(c, cushion):
    """
    Calls the appropriate drawer based on available dimensions.
    Uses safe validation before dispatch.
    """
    try:
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
            draw_curved_cushion(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("top_thickness", "bottom_thickness","height","length")):
            draw_tapered_bolster(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("width", "side_length","middle_length")):
            draw_curved(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("side", "thickness")):
            draw_equilateral_triangle(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "length")):
            name = cushion.get("cushion_name", "").lower()
            if "left" in name:
                draw_left_cushion(c, cushion)
            else:
                draw_right_cushion(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "height","edge")):
            draw_clipped_trapeze(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("top_base", "bottom_base", "height")):
            draw_trapezium(c, cushion)
        elif all(cushion.get(k, 0) > 0 for k in ("width", "length", "thickness")):
            name = cushion.get("cushion_name", "").lower()
            if "triangle" in name:
                draw_right_triangle(c, cushion)
            else:
                draw_rectangle(c, cushion)
        else:
            raise ValueError("Unable to determine cushion shape. Missing or invalid key dimensions.")
    except Exception as e:
        raise ValueError(f"Shape dispatch failed: {str(e)}")

@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        print(f"Received request to /generate-confirmation")
        api_call_number = increment_counter()
        print(f"API call count: {api_call_number}")
        
        print(f"Request headers: {dict(request.headers)}")
        data = request.get_json(force=True)
        print(f"Request data received: {data}")

        # Validate basic input
        cushions = data.get("cushions", [])
        if not cushions:
            return jsonify({"error": "No cushions provided in request"}), 400

        customer_name = data.get('customer_name', 'Unknown')
        order_id = data.get('order_id', 'Unknown')
        email = data.get('email', '')
        shipping_address = data.get('shipping_address', [])
        billing_address = data.get('billing_address', [])

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)

        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        c = canvas.Canvas(filepath, pagesize=letter)
        page_width, page_height = letter

        # ---------- Page 1: Customer Info ----------
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

        # ---------- Cushion Pages ----------
        print(f"Processing {len(cushions)} cushions...")
        margin = 0.75 * inch
        slot_gap = 0.35 * inch  
        slot_count_per_page = 2
        usable_height = page_height - 2 * margin
        slot_height = usable_height / slot_count_per_page
        slot_width = page_width - 2 * margin

        def render_cushion_slot(cushion, slot_index_on_page):
            x0 = margin
            y0 = page_height - margin - (slot_index_on_page + 1) * slot_height

            c.setFont("Helvetica-Bold", 13)
            title = cushion.get("cushion_name", "Cushion").strip() or "Cushion"
            c.drawString(x0, y0 + slot_height - 0.3 * inch, f"{title}")

            c.setStrokeColor(colors.lightgrey)
            c.rect(x0, y0, slot_width, slot_height, stroke=1, fill=0)
            c.setStrokeColor(colors.black)

            inner_pad_x = 0.3 * inch
            inner_pad_y = 0.5 * inch
            c.saveState()
            c.translate(x0 + inner_pad_x, y0 + inner_pad_y)

            try:
                draw_cushion_by_shape(c, cushion)
            except Exception as e:
                c.restoreState()
                c.setFillColor(colors.red)
                c.setFont("Helvetica", 12)
                c.drawString(x0 + inner_pad_x, y0 + inner_pad_y, f"Error drawing cushion: {e}")
                c.setFillColor(colors.black)
                return

            c.restoreState()

        for idx, cushion in enumerate(cushions):
            if idx % slot_count_per_page == 0:
                if idx != 0:
                    c.showPage()

            slot_index = idx % slot_count_per_page
            print(f"Processing cushion {idx+1}: {cushion.get('cushion_name', 'Unnamed')} -> slot {slot_index} on page")
            render_cushion_slot(cushion, slot_index)

        c.save()

        pdf_url = url_for('serve_pdf', filename=filename, _external=True)
        print(f"PDF generated successfully: {filename}")
        print(f"PDF URL: {pdf_url}")
        return jsonify({"pdf_link": pdf_url})

    except Exception as e:
        import sys
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

@app.route('/')
def index():
    return render_template_string(open("form.html").read())

if __name__ == '__main__':
    from reportlab.lib.units import inch
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
