# app2.py
from flask import Flask, request, jsonify, send_from_directory, url_for, render_template_string
from reportlab.lib.pagesizes import letter
import os
import uuid

# --- drawer imports (each on its own line) ---
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

@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        print("Received request to /generate-confirmation")
        api_call_number = increment_counter()
        print(f"API call count: {api_call_number}")

        print(f"Request headers: {dict(request.headers)}")
        data = request.get_json(force=True)
        print(f"Request data received: {data}")

        customer_name = data['customer_name']
        order_id = data['order_id']
        email = data['email']
        shipping_address = data['shipping_address']
        billing_address = data['billing_address']
        cushions = data['cushions']

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)

        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        c = canvas.Canvas(filepath, pagesize=letter)
        page_width, page_height = letter

        # =========================
        # Page 1 - Customer Info
        # =========================
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

        # Next page for cushions
        c.showPage()

        # ==========================================
        # Cushions — 2 per page layout
        # ==========================================
        print(f"Processing {len(cushions)} cushions...")

        SLOTS_PER_PAGE = 2
        MARGIN_X = 0.75 * inch
        MARGIN_Y = 0.75 * inch
        usable_height = page_height - 2 * MARGIN_Y
        usable_width = page_width - 2 * MARGIN_X
        SLOT_HEIGHT = usable_height / SLOTS_PER_PAGE
        SLOT_WIDTH = usable_width

        def draw_slot_guides():
            c.setLineWidth(0.5)
            for s in range(1, SLOTS_PER_PAGE):
                y = MARGIN_Y + s * SLOT_HEIGHT
                c.line(MARGIN_X, y, MARGIN_X + SLOT_WIDTH, y)

        draw_slot_guides()
        slot_in_page = 0  # 0 or 1

        for i, cushion in enumerate(cushions):
            name_for_log = cushion.get('cushion_name', 'Unnamed')
            print(f"Processing cushion {i+1}: {name_for_log}")

            slot_y_bottom = MARGIN_Y + slot_in_page * SLOT_HEIGHT
            slot_x_left = MARGIN_X

            # Heading
            c.saveState()
            c.setFont("Helvetica-Bold", 14)
            heading = cushion.get("cushion_name", f"Cushion {i+1}")
            qty = cushion.get("quantity") or cushion.get("qty")
            heading_text = f"{heading}" + (f"  (Qty: {qty})" if qty else "")
            c.drawString(slot_x_left, slot_y_bottom + SLOT_HEIGHT - 0.3 * inch, heading_text)
            c.restoreState()

            # One-line specs (optional)
            spec_lines = []
            def add_spec(label, key):
                val = cushion.get(key)
                if val not in (None, "", 0):
                    spec_lines.append(f"{label}: {val}")
            add_spec("Fabric", "fabric")
            add_spec("Fill", "fill")
            add_spec("Thickness", "thickness")
            add_spec("Width", "width")
            add_spec("Length", "length")
            add_spec("Top Width", "top_width")
            add_spec("Bottom Width", "bottom_width")
            add_spec("Diameter", "diameter")
            add_spec("Zipper", "zipper_position")

            if spec_lines:
                c.saveState()
                c.setFont("Helvetica", 10)
                text_y = slot_y_bottom + SLOT_HEIGHT - 0.52 * inch
                c.drawString(slot_x_left, text_y, " | ".join(spec_lines[:4]))
                c.restoreState()

            # Translate into slot and draw the shape
            c.saveState()
            c.translate(slot_x_left + 0.25 * inch, slot_y_bottom + 0.25 * inch)
            # c.scale(0.9, 0.9)  # Uncomment if drawings are too large

            # --- routing stays the same ---
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
                draw_tapered_bolster_drawer(c, cushion) if False else draw_tapered_bolster(c, cushion)
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
                raise ValueError("Unable to determine cushion shape. Missing key dimensions.")
            # --- end routing ---

            c.restoreState()

            # Move to next slot / page
            slot_in_page += 1
            if slot_in_page >= SLOTS_PER_PAGE and i != len(cushions) - 1:
                c.showPage()
                slot_in_page = 0
                draw_slot_guides()

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
    # Fallback if form.html isn't present in container
    try:
        return render_template_string(open("form.html").read())
    except Exception:
        return "<h2>Confirmation File Generator</h2><p>POST JSON to /generate-confirmation</p>", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
