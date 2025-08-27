from flask import Flask, request, jsonify, send_from_directory, url_for, render_template_string
from reportlab.lib.pagesizes import letter
import os
import uuid
from pypdf import PdfReader, PdfWriter, Transformation
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
        print(f"Received request to /generate-confirmation")
        # Count API calls
        api_call_number = increment_counter()
        print(f"API call count: {api_call_number}")
        
        # Log request data for debugging
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
        # Generate initial single-cushion-per-page PDF, then 2-up it into final filepath
        raw_filename = f"raw_{uuid.uuid4().hex}.pdf"
        raw_filepath = os.path.join(PDF_DIR, raw_filename)

        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        c = canvas.Canvas(raw_filepath, pagesize=letter)
        page_width, page_height = letter

        # Page 1 - Customer Info
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

        print(f"Processing {len(cushions)} cushions...")
        for i, cushion in enumerate(cushions):
            print(f"Processing cushion {i+1}: {cushion.get('cushion_name', 'Unnamed')}")
            if all(cushion.get(k, 0) > 0 for k in ("length", "top_width", "bottom_width", "ear", "thickness")):
                if cushion.get("top_width") > cushion.get("bottom_width"):
                    print(f"  Drawing T-shape cushion")
                    draw_t_shape(c, cushion)
                else:
                    print(f"  Drawing L-shape cushion")
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
                else : 
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
        # Finish raw PDF and then produce a 2-up final PDF (two cushions per page)
        c.save()

        try:
            reader = PdfReader(raw_filepath)
            writer = PdfWriter()

            # Keep the first page (customer info) as-is
            if len(reader.pages) >= 1:
                writer.add_page(reader.pages[0])

            # 2-up the remaining pages (each originally one cushion per page)
            W, H = letter
            margin_x = 0.5 * 72  # 0.5 inch in points
            margin_y = 0.5 * 72
            # uniform scale to fit two pages vertically and within horizontal margins
            sx = (W - 2 * margin_x) / W
            sy = ((H - 2 * margin_y) / 2) / H
            s = min(sx, sy)

            tx = (W - s * W) / 2
            ty_bottom = margin_y
            ty_top = H - margin_y - s * H

            # Process pages in pairs starting from index 1
            cushion_pages = reader.pages[1:]
            for idx in range(0, len(cushion_pages), 2):
                new_page = writer.add_blank_page(width=W, height=H)

                # Top slot
                top_page = cushion_pages[idx]
                t_top = Transformation().scale(s).translate(tx, ty_top)
                new_page.merge_transformed_page(top_page, t_top)

                # Bottom slot (if exists)
                if idx + 1 < len(cushion_pages):
                    bottom_page = cushion_pages[idx + 1]
                    t_bottom = Transformation().scale(s).translate(tx, ty_bottom)
                    new_page.merge_transformed_page(bottom_page, t_bottom)

            with open(filepath, "wb") as f_out:
                writer.write(f_out)
        finally:
            # Cleanup raw file
            try:
                os.remove(raw_filepath)
            except Exception:
                pass

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
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
