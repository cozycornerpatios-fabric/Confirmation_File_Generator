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
from left_cushion_drawer import draw_left_cushion

# NEW: background execution + job store
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.url_map.strict_slashes = False 

# Where PDFs are stored
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

# Background pool and in-memory job store (swap with Redis for durability)
EXECUTOR = ThreadPoolExecutor(max_workers=4)
JOBS = {}  # {job_id: {"status": "queued|running|done|error", "pdf_link": str, "error": str}}

@app.route('/', methods=['GET', 'HEAD'])
def health_or_index():
    """Keep your old index, serve a basic health too."""
    # If you have a form.html, keep rendering it on GET
    if request.method == 'GET' and os.path.exists('form.html'):
        return render_template_string(open('form.html').read())
    return 'ok', 200

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"ok": True}), 200

# -------------------- BACKGROUND WORKER --------------------
def build_pdf(job_id: str, payload: dict, base_url: str):
    """Heavy PDF generation executed in a background thread."""
    JOBS[job_id]["status"] = "running"
    try:
        # Extract payload
        customer_name = payload['customer_name']
        order_id = payload['order_id']
        email = payload['email']
        shipping_address = payload['shipping_address']
        billing_address = payload['billing_address']
        cushions = payload['cushions']

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)

        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        c = canvas.Canvas(filepath, pagesize=letter)
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

        # ====== Layout constants ======
        PAGE_W, PAGE_H = letter
        MARGIN_L = 0.75 * inch
        MARGIN_R = 0.5 * inch
        MARGIN_T = 0.6 * inch
        MARGIN_B = 0.6 * inch

        # Two stacked sections per page
        SECTION_GAP = 0.35 * inch
        AVAILABLE_H = PAGE_H - MARGIN_T - MARGIN_B - SECTION_GAP
        SECTION_H = AVAILABLE_H / 2.0

        # Columns inside each section
        COL_GAP = 0.35 * inch
        LEFT_COL_W = 3.3 * inch           # details
        RIGHT_COL_W = PAGE_W - MARGIN_L - MARGIN_R - COL_GAP - LEFT_COL_W  # diagram
        DETAILS_LINE_H = 0.2 * inch

        # If your draw_* functions were built for a full page,
        # scale them down to fit the right column area:
        DIAGRAM_SCALE = min(
            RIGHT_COL_W / (7.5 * inch),   # assume original width used by drawers
            (SECTION_H - 0.2 * inch) / (4.5 * inch)  # assume original height
        )

        def shape_router(cnv, cushion):
            """
            Calls the correct drawer based on the same rules you had.
            We rely on translate/scale to position it, so drawers can stay unchanged.
            """
            if all(cushion.get(k, 0) > 0 for k in ("length", "top_width", "bottom_width", "ear", "thickness")):
                if cushion.get("top_width") > cushion.get("bottom_width"):
                    draw_t_shape(cnv, cushion)
                else:
                    draw_l_shape(cnv, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("diameter", "thickness")):
                name = cushion.get("cushion_name", "").lower()
                if "semi" in name:
                    draw_semi_round(cnv, cushion)
                else:
                    draw_round(cnv, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("front_width_straight", "back_width_straight","thickness","front_width_curved","back_width_curved")):
                draw_curved_cushion(cnv,cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_thickness", "bottom_thickness","height","length")):
                draw_tapered_bolster(cnv,cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("width", "side_length","middle_length")):
                draw_curved(cnv,cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("side", "thickness")):
                draw_equilateral_triangle(cnv, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "length")):
                name = cushion.get("cushion_name", "").lower()
                if "left" in name:
                    draw_left_cushion(cnv, cushion)
                else:
                    draw_right_cushion(cnv,cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "height","edge")):
                draw_clipped_trapeze(cnv,cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_base", "bottom_base", "height")):
                draw_trapezium(cnv, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("width", "length", "thickness")):
                name = cushion.get("cushion_name", "").lower()
                if "triangle" in name:
                    draw_right_triangle(cnv, cushion)
                else:
                    draw_rectangle(cnv, cushion)
            else:
                raise ValueError("Unable to determine cushion shape. Missing key dimensions.")

        def draw_cushion_section(cnv, cushion, section_index_on_page):
            """
            section_index_on_page: 0 for top section, 1 for bottom section
            """
            # --- section frame (y extents)
            section_top_y = PAGE_H - MARGIN_T - (SECTION_H + SECTION_GAP) * section_index_on_page
            section_bottom_y = section_top_y - SECTION_H

            # --- left column: details
            x_details = MARGIN_L
            y_details = section_top_y - 0.15 * inch

            # Title
            cnv.setFont("Helvetica-Bold", 14)
            title = cushion.get("cushion_name", "Cushion")
            qty = cushion.get("quantity", 1)
            cnv.drawString(x_details, y_details, f"Title : {title}")
            y_details -= DETAILS_LINE_H
            cnv.setFont("Helvetica-Bold", 12)
            cnv.drawString(x_details, y_details, f"Quantity : {qty}")
            y_details -= DETAILS_LINE_H

            # Body details (show present keys in a friendly order)
            cnv.setFont("Helvetica", 11)
            def pr(label, key):
                nonlocal y_details
                val = cushion.get(key)
                if val not in (None, "", []):
                    cnv.drawString(x_details, y_details, f"{label} : {val}")
                    y_details -= DETAILS_LINE_H

            ordered = [
                ("Length", "length"),
                ("Bottom Width", "bottom_width"),
                ("Top Width", "top_width"),
                ("Thickness", "thickness"),
                ("Fill", "fill"),
                ("Piping", "piping"),
                ("Ties", "ties"),
                ("Fabric", "fabric"),
                ("Zipper Position", "zipper_position")
            ]
            for lbl, key in ordered:
                pr(lbl, key)

            # --- right column: diagram
            x_diagram_origin = MARGIN_L + LEFT_COL_W + COL_GAP
            y_diagram_origin = section_bottom_y + 0.25 * inch  # a little padding

            cnv.saveState()
            # Move origin to right column area and scale down
            cnv.translate(x_diagram_origin, y_diagram_origin)
            if DIAGRAM_SCALE < 1.0:
                cnv.scale(DIAGRAM_SCALE, DIAGRAM_SCALE)

            # Let your existing router draw relative to the new origin
            shape_router(cnv, cushion)
            cnv.restoreState()

            # Optional: a faint separator line between sections
            if section_index_on_page == 0:
                cnv.setLineWidth(0.5)
                cnv.setDash(1,2)
                cnv.line(MARGIN_L, section_bottom_y, PAGE_W - MARGIN_R, section_bottom_y)
                cnv.setDash([])

        # ====== Iterate cushions: two per page ======
        print(f"Processing {len(cushions)} cushions...")
        for idx, cushion in enumerate(cushions):
            section_idx = idx % 2  # 0 top, 1 bottom
            print(f"Processing cushion {idx+1}: {cushion.get('cushion_name', 'Unnamed')} (section {section_idx})")
            draw_cushion_section(c, cushion, section_idx)
            # After bottom section, start a new page
            if section_idx == 1 and idx != len(cushions) - 1:
                c.showPage()

        c.save()

        # Build public link (avoid url_for in background threads)
        base = base_url.rstrip('/')  # e.g., https://confirmation-file.onrender.com
        pdf_link = f"{base}/pdfs/{filename}"
        JOBS[job_id].update(status="done", pdf_link=pdf_link)

    except Exception as e:
        JOBS[job_id].update(status="error", error=str(e))

# -------------------- API ENDPOINTS --------------------
@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        print("Received request to /generate-confirmation")
        
        # Parse JSON
        data = request.get_json(force=True)
        print(f"Request data received: {data}")

        # Minimal validation (keep/exted as needed)
        required = ["customer_name", "order_id", "email", "shipping_address", "billing_address", "cushions"]
        missing = [k for k in required if k not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        # Create a job and run in background
        job_id = uuid.uuid4().hex
        JOBS[job_id] = {"status": "queued"}

        # Capture base URL now (request context won't exist later)
        base_url = request.url_root
        EXECUTOR.submit(build_pdf, job_id, data, base_url)

        # Return immediately to avoid GPT hang
        return jsonify({"job_id": job_id, "status": "queued"}), 200

    except Exception as e:
        import sys
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    resp = {"job_id": job_id, "status": job["status"]}
    if "pdf_link" in job:
        resp["pdf_link"] = job["pdf_link"]
    if "error" in job:
        resp["error"] = job["error"]
    return jsonify(resp), 200

# Keep the legacy index route if you want a form
# (Handled by health_or_index above)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # For local testing only. In Render, use Gunicorn (see Start Command).
    app.run(debug=True, host='0.0.0.0', port=port)
