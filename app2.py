from flask import Flask, request, jsonify, send_from_directory, url_for, render_template_string
import os
import uuid
import time, sys
from concurrent.futures import ThreadPoolExecutor

# --- FAST ReportLab imports at module load (avoid per-job import cost)
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# --- drawing imports (your existing modules)
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

app = Flask(__name__)

# Boot banner + version
BUILD_TS = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print(f"[BOOT] app2.py loaded @ {BUILD_TS}", file=sys.stdout, flush=True)

# Accept both with/without trailing slash
app.url_map.strict_slashes = False

# Where PDFs are stored (use /tmp for faster I/O on Render)
PDF_DIR = "/tmp/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def _new_canvas(filepath: str):
    # Enable PDF compression for smaller/faster output
    return rl_canvas.Canvas(filepath, pagesize=letter, pageCompression=1)

# Background pool and in-memory job store (swap for Redis if you want durability)
EXECUTOR = ThreadPoolExecutor(max_workers=4)
JOBS = {}  # job_id -> {"status": "queued|running|done|error", "pdf_link": str, "error": str}

# --------- Utility/debug routes ----------
@app.route('/__routes', methods=['GET'])
def __routes():
    rules = sorted([f"{sorted(list(r.methods))} {r.rule}" for r in app.url_map.iter_rules()])
    return jsonify({"routes": rules, "build_ts": BUILD_TS}), 200

@app.route('/version', methods=['GET'])
def version():
    return jsonify({"build_ts": BUILD_TS, "note": "generate-confirmation returns 200"}), 200

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"ok": True}), 200

@app.route('/', methods=['GET', 'HEAD'])
def health_or_index():
    if request.method == 'GET' and os.path.exists('form.html'):
        return render_template_string(open('form.html').read())
    return 'ok', 200

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

# --------- Background worker ----------
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

        c = _new_canvas(filepath)
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

        # Cushion pages (your existing branching)
        for i, cushion in enumerate(cushions):
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
            elif all(cushion.get(k, 0) > 0 for k in ("front_width_straight", "back_width_straight", "thickness", "front_width_curved", "back_width_curved")):
                draw_curved_cushion(c, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_thickness", "bottom_thickness", "height", "length")):
                draw_tapered_bolster(c, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("width", "side_length", "middle_length")):
                draw_curved(c, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("side", "thickness")):
                draw_equilateral_triangle(c, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "length")):
                name = cushion.get("cushion_name", "").lower()
                if "left" in name:
                    draw_left_cushion(c, cushion)
                else:
                    draw_right_cushion(c, cushion)
            elif all(cushion.get(k, 0) > 0 for k in ("top_width", "bottom_width", "height", "edge")):
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

        c.save()

        base = base_url.rstrip('/')  # e.g., https://confirmation-file.onrender.com
        pdf_link = f"{base}/pdfs/{filename}"
        JOBS[job_id].update(status="done", pdf_link=pdf_link)

    except Exception as e:
        JOBS[job_id].update(status="error", error=str(e))

# --------- SYNC fast-path endpoint (instant PDF for simple single cushion) ----------
@app.route('/generate-confirmation-sync', methods=['POST'])
def generate_confirmation_sync():
    data = request.get_json(force=True)

    # Basic validation
    required = ["customer_name","order_id","email","shipping_address","billing_address","cushions"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    cushions = data.get("cushions", [])
    if len(cushions) != 1:
        return jsonify({"error": "sync endpoint supports exactly 1 cushion"}), 400

    cz = cushions[0]
    shape = (cz.get("shape") or "").lower()
    is_rect = shape == "rectangle" and all(cz.get(k,0)>0 for k in ("length","width","thickness"))
    is_round = shape == "round" and all(cz.get(k,0)>0 for k in ("diameter","thickness"))
    if not (is_rect or is_round):
        return jsonify({"error":"sync only supports rectangle or round cushions with numeric dimensions"}), 400

    # Generate PDF inline (fast path)
    filename = f"confirmation_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    c = _new_canvas(filepath)
    page_width, page_height = letter

    # Header + customer info
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, page_height-72, "ORDER CONFIRMATION (FAST)")
    c.setFont("Helvetica", 11)
    y = page_height - 100
    for label, val in [("Customer",data["customer_name"]),("Order",data["order_id"]),("Email",data["email"])]:
        c.drawString(72, y, f"{label}: {val}")
        y -= 16

    # One cushion page
    c.showPage()
    if is_rect:
        draw_rectangle(c, cz)
    else:
        draw_round(c, cz)

    c.save()
    base = request.url_root.rstrip('/')
    return jsonify({"pdf_link": f"{base}/pdfs/{filename}", "mode": "sync"}), 200

# --------- API endpoints (async flow) ----------
@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    try:
        data = request.get_json(force=True)

        required = ["customer_name", "order_id", "email", "shipping_address", "billing_address", "cushions"]
        missing = [k for k in required if k not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        job_id = uuid.uuid4().hex
        JOBS[job_id] = {"status": "queued"}

        base_url = request.url_root
        EXECUTOR.submit(build_pdf, job_id, data, base_url)

        # immediate return keeps Actions client responsive
        return jsonify({"job_id": job_id, "status": "queued"}), 200

    except Exception as e:
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

# --- smaller, faster status (matches schema getStatusLite)
@app.route('/status-lite/<job_id>', methods=['GET'])
def status_lite(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"status": "not_found"}), 404
    st = job.get("status", "queued")
    if st == "done":
        return jsonify({"status": "done", "pdf_link": job.get("pdf_link")}), 200
    if st == "error":
        return jsonify({"status": "error", "error": job.get("error")}), 200
    return jsonify({"status": st}), 200

# --- short wait to reduce polling (matches schema awaitJob)
@app.route('/await/<job_id>', methods=['GET'])
def await_job(job_id):
    t0 = time.time()
    while time.time() - t0 < 8:  # wait up to ~8 seconds
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"status": "not_found"}), 404
        st = job.get("status")
        if st in ("done", "error"):
            resp = {"status": st}
            if "pdf_link" in job: resp["pdf_link"] = job["pdf_link"]
            if "error" in job: resp["error"] = job["error"]
            return jsonify(resp), 200
        time.sleep(0.5)
    # still running after short wait
    return jsonify({"status": JOBS.get(job_id, {}).get("status", "queued")}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
