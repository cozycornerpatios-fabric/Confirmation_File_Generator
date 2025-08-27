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

            # Build a base PDF with left-column specs for each 2-up page
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.units import inch

            W, H = letter
            left_margin = 0.5 * inch
            right_margin = 0.5 * inch
            top_margin = 0.5 * inch
            bottom_margin = 0.5 * inch
            usable_width = W - (left_margin + right_margin)
            usable_height = H - (top_margin + bottom_margin)
            half_height = usable_height / 2.0

            text_col_width = usable_width * 0.42  # left column
            gutter = usable_width * 0.03
            diagram_w = usable_width - text_col_width - gutter
            diagram_h = half_height

            base_filename = f"layout_{uuid.uuid4().hex}.pdf"
            base_filepath = os.path.join(PDF_DIR, base_filename)
            bc = rl_canvas.Canvas(base_filepath, pagesize=letter)

            def draw_specs_block(cnv, cushion, origin_y):
                y = origin_y
                x = left_margin
                cnv.setFont("Helvetica-Bold", 14)
                title = cushion.get("cushion_name", "Cushion")
                qty = cushion.get("quantity", 1)
                cnv.drawString(x, y, f"Title : {title}")
                y -= 0.28 * inch
                cnv.setFont("Helvetica-Bold", 12)
                cnv.drawString(x, y, f"Quantity : {qty}")
                y -= 0.28 * inch

                fields_order = [
                    ("length", "Length"),
                    ("width", "Width"),
                    ("bottom_width", "Bottom Width"),
                    ("top_width", "Top Width"),
                    ("ear", "Ear"),
                    ("height", "Height"),
                    ("side", "Side"),
                    ("side_length", "Side Length"),
                    ("middle_length", "Middle Length"),
                    ("diameter", "Diameter"),
                    ("top_base", "Top Base"),
                    ("bottom_base", "Bottom Base"),
                    ("edge", "Clipping Edge"),
                    ("top_thickness", "Top Thickness"),
                    ("bottom_thickness", "Bottom Thickness"),
                    ("thickness", "Thickness"),
                    ("fill", "Fill"),
                    ("fabric", "Fabric"),
                    ("fabric_collection", "Fabric Collection"),
                    ("fabric_option", "Fabric Option"),
                    ("piping", "Piping"),
                    ("ties", "Ties"),
                    ("zipper", "Zipper Position"),
                ]

                cnv.setFont("Helvetica", 12)
                for key, label in fields_order:
                    if key in cushion and cushion[key] not in (None, ""):
                        value = cushion[key]
                        cnv.drawString(x, y, f"{label} : {value}")
                        y -= 0.24 * inch

            # number of 2-up pages to create
            cushion_pages = reader.pages[1:]
            num_pairs = (len(cushions) + 1) // 2
            for pair_index in range(num_pairs):
                # Page header
                header_y = H - top_margin
                bc.setFont("Helvetica-Bold", 24)
                bc.drawString(left_margin, header_y, "Item Details")

                # top cushion specs (under header)
                top_idx = pair_index * 2
                top_specs_y = header_y - 0.45 * inch
                draw_specs_block(bc, cushions[top_idx], top_specs_y)

                # bottom cushion specs (start at top of bottom half)
                bottom_specs_y = bottom_margin + half_height - 0.25 * inch
                if top_idx + 1 < len(cushions):
                    draw_specs_block(bc, cushions[top_idx + 1], bottom_specs_y)
                bc.showPage()
            bc.save()

            base_reader = PdfReader(base_filepath)

            # Compose final pages: start from base pages and overlay cropped diagrams on right
            for pair_page_idx in range(num_pairs):
                composed = base_reader.pages[pair_page_idx]
                new_page = writer.add_page(composed)

                # Slot origins for right-side diagrams
                right_x0 = left_margin + text_col_width + gutter
                top_y0 = H - top_margin - diagram_h
                bottom_y0 = bottom_margin

                # Source page size
                src_W, src_H = W, H
                # crop left part to hide specs text from drawers
                left_crop_ratio = 0.35
                left_crop_pts = src_W * left_crop_ratio
                visible_src_w = src_W - left_crop_pts

                # Top diagram
                src_idx = pair_page_idx * 2
                if src_idx < len(cushion_pages):
                    top_page = cushion_pages[src_idx]
                    # Apply cropbox to show only right portion
                    try:
                        top_page.cropbox.lower_left = (left_crop_pts, 0)
                        top_page.cropbox.upper_right = (src_W, src_H)
                    except Exception:
                        pass
                    s_top = min(diagram_w / visible_src_w, diagram_h / src_H)
                    t_top = (
                        Transformation()
                        .scale(s_top)
                        .translate(right_x0 - s_top * left_crop_pts, top_y0)
                    )
                    new_page.merge_transformed_page(top_page, t_top)

                # Bottom diagram
                if src_idx + 1 < len(cushion_pages):
                    bottom_page = cushion_pages[src_idx + 1]
                    try:
                        bottom_page.cropbox.lower_left = (left_crop_pts, 0)
                        bottom_page.cropbox.upper_right = (src_W, src_H)
                    except Exception:
                        pass
                    s_bottom = min(diagram_w / visible_src_w, diagram_h / src_H)
                    t_bottom = (
                        Transformation()
                        .scale(s_bottom)
                        .translate(right_x0 - s_bottom * left_crop_pts, bottom_y0)
                    )
                    new_page.merge_transformed_page(bottom_page, t_bottom)

            with open(filepath, "wb") as f_out:
                writer.write(f_out)
        finally:
            # Cleanup raw file
            try:
                os.remove(raw_filepath)
            except Exception:
                pass
            # Cleanup base layout
            try:
                os.remove(base_filepath)
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
