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
        # Page 1 - Customer Info + Cushion Details (on same page)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(1 * inch, page_height - 1 * inch, "ORDER CONFIRMATION")

        y_left = page_height - 1.6 * inch
        left_x = 1.0 * inch
        val_x  = 2.8 * inch
        line_gap = 0.25 * inch
        bottom_margin = 0.8 * inch
        
        def kv_line(label, value):
            nonlocal y_left
            if y_left < bottom_margin + line_gap:
                c.showPage()
                c.setFont("Helvetica-Bold", 20)
                c.drawString(1 * inch, page_height - 1 * inch, "ORDER CONFIRMATION")
                y_left = page_height - 1.6 * inch
            if label:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(left_x, y_left, f"{label}:")
                c.setFont("Helvetica", 12)
                c.drawString(val_x, y_left, str(value))
            else:
                c.setFont("Helvetica", 12)
                c.drawString(left_x + 0.2 * inch, y_left, str(value))
            y_left -= line_gap

        # ---- Customer/Billing blocks
        details = [
            ("Customer Name", customer_name),
            ("Order Number", order_id),
            ("Email", email),
            ("Shipping Address", ""),
        ] + [("", line) for line in shipping_address] + [
            ("Billing Address", ""),
        ] + [("", line) for line in billing_address]
        
        for label, value in details:
            kv_line(label, value)

        # ---- Divider + Cushion Details heading
        y_left -= 0.10 * inch
        if y_left < bottom_margin + 1.0 * inch:
            c.showPage()
            c.setFont("Helvetica-Bold", 20)
            c.drawString(1 * inch, page_height - 1 * inch, "ORDER CONFIRMATION")
            y_left = page_height - 1.6 * inch
        
        c.setLineWidth(0.5)
        c.line(left_x, y_left, page_width - 1.0 * inch, y_left)
        y_left -= 0.3 * inch

        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_x, y_left, "Cushion Details")
        y_left -= 0.35 * inch

        # ---- Print a compact spec list for each cushion
        from reportlab.pdfbase.pdfmetrics import stringWidth
        max_text_width = (page_width - 1.0 * inch) - left_x

        def wrapped_value(label, value):
            """Draw label: value with simple word-wrap for long values (e.g., fabric)."""
            nonlocal y_left
            lab = f"{label}: "
            c.setFont("Helvetica-Bold", 12)
            lab_w = stringWidth(lab, "Helvetica-Bold", 12)
            c.drawString(left_x, y_left, lab)
            c.setFont("Helvetica", 12)
            words = str(value).split()
            line = ""
            while words:
                test = (line + " " + words[0]).strip()
                if stringWidth(lab + test, "Helvetica", 12) <= max_text_width:
                    line = test
                    words.pop(0)
                    if not words:
                        c.drawString(left_x + lab_w, y_left, line)
                        y_left -= 0.20 * inch
                else:
                    c.drawString(left_x + lab_w, y_left, line)
                    y_left -= 0.20 * inch
                    line = ""
                    lab_w = 0  # subsequent wrapped lines have no bold label

        for i, cu in enumerate(cushions, 1):
            if y_left < bottom_margin + 1.0 * inch:
                c.showPage()
                c.setFont("Helvetica-Bold", 20)
                c.drawString(1 * inch, page_height - 1 * inch, "ORDER CONFIRMATION")
                y_left = page_height - 1.6 * inch
                c.setFont("Helvetica-Bold", 16)
                c.drawString(left_x, y_left, "Cushion Details (cont.)")
                y_left -= 0.35 * inch

            # Cushion header
            name = cu.get("cushion_name") or cu.get("name", "")
            c.setFont("Helvetica-Bold", 13)
            c.drawString(left_x, y_left, f"Cushion {i}" + (f" — {name}" if name else ""))
            y_left -= 0.22 * inch

            # Pick common keys to show (only if present & non-zero)
            show_keys = [
                ("Shape", None),  # derive from name if you want, optional
                ("Length", cu.get("length")),
                ("Width", cu.get("width")),
                ("Top Width", cu.get("top_width")),
                ("Bottom Width", cu.get("bottom_width")),
                ("Height", cu.get("height")),
                ("Diameter", cu.get("diameter")),
                ("Thickness", cu.get("thickness") or cu.get("top_thickness") or cu.get("bottom_thickness")),
                ("Zipper Position", cu.get("zipper")),
                ("Piping", cu.get("piping")),
                ("Ties", cu.get("ties")),
                ("Quantity", cu.get("quantity")),
                ("Fill", cu.get("fill")),
                ("Fabric", cu.get("fabric")),
            ]

            for label, value in show_keys:
                if value in (None, "", 0, "0"):
                    continue
                # Fabric can be long → wrap it
                if label == "Fabric":
                    wrapped_value(label, value)
                else:
                    kv_line(label, value)
        
            y_left -= 0.08 * inch  # small spacing between cushions

# Now advance to the next page for your diagram pages
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

            # Adaptive N-up (try 3-up to reduce whitespace, else 2-up)
            W, H = letter
            margin_x = 0.20 * 72  # ~0.20 inch for larger content
            margin_y = 0.20 * 72

            def compute_scale(slots):
                sx = (W - 2 * margin_x) / W
                sy = ((H - 2 * margin_y) / slots) / H
                return min(sx, sy)

            # Force two cushions per page so each new cushion starts at page top.
            slots_per_page = 2

            # Slot dimensions (target area for each cushion diagram)
            slot_w = W - 2 * margin_x
            slot_h = (H - 2 * margin_y) / slots_per_page

            # Precompute slot top edges (top-down order) so first cushion starts at page top
            slots_top_y = [H - margin_y - i * slot_h for i in range(slots_per_page)]

            # Layout: specs on left, diagram on right with a small gutter so they are close
            text_ratio = 0.28
            gutter_x = 0.18 * 72  # wider gap to keep text out of diagram
            text_w = slot_w * text_ratio
            diagram_w_target = slot_w - text_w - gutter_x

            # Create base pages with specs in the left column for each slot
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib.units import inch
            base_filename = f"layout_{uuid.uuid4().hex}.pdf"
            base_filepath = os.path.join(PDF_DIR, base_filename)
            bc = rl_canvas.Canvas(base_filepath, pagesize=letter)

            def _derive_shape_label(cushion):
                try:
                    # Clipped trapeze first (has explicit edge)
                    if all(float(cushion.get(k, 0)) > 0 for k in ("top_width", "bottom_width", "height")) and cushion.get("edge") not in (None, "", 0, "0"):
                        return "Clipped Trapeze"
                    if all(float(cushion.get(k, 0)) > 0 for k in ("top_base", "bottom_base", "height")):
                        return "Trapezoid"
                    if all(float(cushion.get(k, 0)) > 0 for k in ("length", "top_width", "bottom_width", "ear", "thickness")):
                        return "T-Shape" if cushion.get("top_width") > cushion.get("bottom_width") else "L-Shape"
                    if all(float(cushion.get(k, 0)) > 0 for k in ("diameter", "thickness")):
                        return "Round"
                except Exception:
                    pass
                return None

            def _thickness_value(cushion):
                # Try common keys for thickness across shapes
                for key in ("thickness", "thickness_in", "top_thickness", "bottom_thickness"):
                    if key in cushion and cushion[key] not in (None, ""):
                        try:
                            val = float(cushion[key])
                            return f"{val:g}\""
                        except Exception:
                            return str(cushion[key])
                return None

            def _draw_wrapped_kv(cnv, x, y, label, value, max_width):
                from reportlab.pdfbase.pdfmetrics import stringWidth
                label_text = f"{label} : "
                font_label = ("Helvetica-Bold", 12)
                font_value = ("Helvetica", 12)
                line_height = 0.20 * 72

                # Measure label width
                label_w = stringWidth(label_text, font_label[0], font_label[1])
                value_w_max = max_width - label_w

                # Split value into words and wrap
                words = str(value).split()
                line = ""

                cnv.setFont(*font_label)
                cnv.drawString(x, y, label_text)
                cnv.setFont(*font_value)

                def draw_value_line(text, yy):
                    # Draw the wrapped value line; width control handled by pre-wrap calculation
                    cnv.drawString(x + label_w, yy, text)

                for word in words:
                    test = (line + " " + word).strip()
                    if stringWidth(test, font_value[0], font_value[1]) <= value_w_max:
                        line = test
                    else:
                        draw_value_line(line, y)
                        y -= line_height
                        line = word
                if line:
                    draw_value_line(line, y)
                    y -= line_height

                return y - 4  # extra spacing between rows

            def draw_specs_block(cnv, cushion, slot_top_y):
                x = margin_x
                y = slot_top_y - 0.15 * inch
                cnv.setFont("Helvetica-Bold", 14)

                shape_label = _derive_shape_label(cushion)

                # For Trapezoid, print the exact ordered block requested
                if shape_label == "Trapezoid":
                    fields_order = [
                        ("__shape__", "Shape"),
                        ("top_base", "Top Base"),
                        ("bottom_base", "Bottom Base"),
                        ("height", "Height"),
                        ("thickness", "Thickness"),
                        ("zipper", "Zipper Position"),
                        ("piping", "Piping"),
                        ("ties", "Ties"),
                        ("quantity", "Quantity"),
                        ("fill", "Fill"),
                        ("fabric", "Fabric"),
                    ]
                else:
                    # Generic fallback (hide zeros), include zipper
                    fields_order = [
                        ("__shape__", "Shape"),
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
                        ("zipper", "Zipper Position"),
                        ("piping", "Piping"),
                        ("ties", "Ties"),
                        ("quantity", "Quantity"),
                        ("fill", "Fill"),
                        ("fabric", "Fabric"),
                    ]

                for key, label in fields_order:
                    if key not in cushion:
                        if key == "__shape__":
                            val = shape_label or cushion.get("cushion_name", "")
                        else:
                            continue
                    else:
                        val = cushion[key]
                    # Skip empty or zero values
                    if val is None:
                        continue
                    try:
                        if isinstance(val, (int, float)) and float(val) == 0:
                            continue
                        if isinstance(val, str) and val.strip() == "0":
                            continue
                    except Exception:
                        pass
                    # Ensure long Fabric stays in left column, not diagram
                    y = _draw_wrapped_kv(cnv, x, y, label, val, text_w - 2)

            # Build base pages
            total = len(cushions)
            page_count = (total + slots_per_page - 1) // slots_per_page
            for p in range(page_count):
                for si in range(slots_per_page):
                    idx = p * slots_per_page + si
                    if idx >= total:
                        break
                    # Top y for this slot (top-down)
                    slot_top_y = slots_top_y[si]
                    draw_specs_block(bc, cushions[idx], slot_top_y)

                    # Thickness label is rendered inside each drawer; do not overlay to avoid duplicates
                bc.showPage()
            bc.save()

            base_reader = PdfReader(base_filepath)

            # Process cushion pages starting from index 1 (skip cover) and compose onto base pages
            cushion_pages = reader.pages[1:]
            for p in range(page_count):
                new_page = writer.add_page(base_reader.pages[p])
                for si in range(slots_per_page):
                    pi = p * slots_per_page + si
                    if pi >= len(cushion_pages):
                        break
                    src_page = cushion_pages[pi]

                    # Trim source page to remove the drawer's own header/specs.
                    # Use tighter crops for trapezoid pages to maximize diagram size.
                    current_cushion = cushions[pi] if pi < len(cushions) else {}
                    shape_lbl = _derive_shape_label(current_cushion)

                    if shape_lbl == "Trapezoid":
                        # Trim more on the left to remove stray partial thickness text (e.g., just '3')
                        left_trim   = 0.95 * 72
                        right_trim  = 0.70 * 72
                        bottom_trim = 0.25 * 72
                        top_trim    = H * 0.60
                    else:
                        side_trim_in = 0.40
                        left_trim   = side_trim_in * 72
                        right_trim  = side_trim_in * 72
                        bottom_trim = side_trim_in * 72
                        top_trim    = H * 0.45

                    try:
                        src_page.cropbox.lower_left  = (left_trim, bottom_trim)
                        src_page.cropbox.upper_right = (W - right_trim, H - top_trim)
                    except Exception:
                        pass

                    visible_w = W - left_trim - right_trim
                    visible_h = H - top_trim - bottom_trim

                    # Scale to fit the diagram region on the right side
                    s_local = min(diagram_w_target / visible_w, slot_h / visible_h)

                    # Place diagram flush against the text column with a small gutter,
                    # top-aligned to the slot so it stays parallel with details.
                    right_x0 = margin_x + text_w + gutter_x
                    tx = right_x0 - s_local * left_trim
                    top_pad = 0.10 * 72  # ~0.10 inch
                    slot_top_y = slots_top_y[si]
                    # Inner safety padding to ensure labels like thickness don’t touch slot edges
                    inner_pad_top = 0.06 * 72
                    inner_pad_bottom = 0.06 * 72
                    ty = (
                        slot_top_y
                        - top_pad
                        - inner_pad_top
                        - (s_local * visible_h)
                        - s_local * bottom_trim
                        + inner_pad_bottom
                    )

                    t = Transformation().scale(s_local).translate(tx, ty)
                    new_page.merge_transformed_page(src_page, t)

            # cleanup base layout file
            try:
                os.remove(base_filepath)
            except Exception:
                pass

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
