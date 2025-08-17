from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import uuid
import time, sys
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# ==== FAST ReportLab imports at module load (avoid per-request import cost)
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import utils as rl_utils

# ==== your existing drawing modules (kept intact)
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

# ---------------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------------
app = Flask(__name__)
app.url_map.strict_slashes = False
BUILD_TS = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
print(f"[BOOT] app2.py loaded @ {BUILD_TS}", file=sys.stdout, flush=True)

# Filesystem
PDF_DIR = os.environ.get("PDF_DIR", "/tmp/pdfs")
os.makedirs(PDF_DIR, exist_ok=True)
LOGO_PATH = os.environ.get("PDF_LOGO_PATH", "")  # optional logo

# Thread pool (tuned):
MAX_WORKERS = int(os.environ.get("PDF_WORKERS", "4"))
EXECUTOR = ThreadPoolExecutor(max_workers=MAX_WORKERS)
JOBS: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------
def _new_canvas(filepath: str):
    """Create a compressed PDF canvas with Letter size."""
    return rl_canvas.Canvas(filepath, pagesize=letter, pageCompression=1)

PAGE_W, PAGE_H = letter
MARGIN_L = 1 * inch
MARGIN_R = 1 * inch
MARGIN_T = 1 * inch
MARGIN_B = 0.9 * inch


def _draw_logo(c):
    if LOGO_PATH and os.path.exists(LOGO_PATH):
        try:
            # Keep logo small and cache scaled dimensions
            c.drawImage(LOGO_PATH, MARGIN_L, PAGE_H - MARGIN_T + 0.1 * inch, width=0.9 * inch, height=0.9 * inch, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass


def _kv(c, x, y, k, v, k_font=("Helvetica-Bold", 11), v_font=("Helvetica", 11)):
    c.setFont(*k_font)
    c.drawString(x, y, f"{k}:")
    c.setFont(*v_font)
    c.drawString(x + 1.8 * inch, y, v)


def _multilines(c, x, y, lines: List[str], leading=14):
    yy = y
    for line in lines:
        if line:
            c.drawString(x, yy, line)
            yy -= leading
    return yy


def _page_header(c, title="ORDER CONFIRMATION"):
    _draw_logo(c)
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - MARGIN_T + 0.2 * inch, title)
    c.setLineWidth(0.7)
    c.line(MARGIN_L, PAGE_H - MARGIN_T - 0.1 * inch, PAGE_W - MARGIN_R, PAGE_H - MARGIN_T - 0.1 * inch)


def _page_footer(c):
    c.setFont("Helvetica", 8)
    c.setFillGray(0.3)
    c.drawString(MARGIN_L, MARGIN_B - 0.5 * inch, f"Generated: {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}")
    c.drawRightString(PAGE_W - MARGIN_R, MARGIN_B - 0.5 * inch, "ZIPCushions")
    c.setFillGray(0)


# ---------------------------------------------------------------------------------
# PDF Builder (background task)
# ---------------------------------------------------------------------------------

def build_pdf(job_id: str, payload: dict, base_url: str):
    JOBS[job_id]["status"] = "running"
    try:
        # ---------- Extract payload ----------
        customer_name = payload.get('customer_name', '')
        order_id = payload.get('order_id', '')
        email = payload.get('email', '')
        shipping_address = payload.get('shipping_address', []) or []
        billing_address = payload.get('billing_address', []) or []
        cushions = payload.get('cushions', []) or []

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        c = _new_canvas(filepath)

        # ---------- Page 1: Customer + Order ----------
        _page_header(c, "ORDER CONFIRMATION")
        y = PAGE_H - MARGIN_T - 0.35 * inch
        c.setFont("Helvetica", 11)
        _kv(c, MARGIN_L, y, "Customer Name", customer_name); y -= 16
        _kv(c, MARGIN_L, y, "Order Number", order_id); y -= 16
        _kv(c, MARGIN_L, y, "Email", email); y -= 22

        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_L, y, "Shipping Address:")
        c.setFont("Helvetica", 11)
        y -= 14
        y = _multilines(c, MARGIN_L + 12, y, shipping_address)
        y -= 10

        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN_L, y, "Billing Address:")
        c.setFont("Helvetica", 11)
        y -= 14
        y = _multilines(c, MARGIN_L + 12, y, billing_address)

        _page_footer(c)
        c.showPage()

        # ---------- Cushion pages ----------
        for cz in cushions:
            _page_header(c, cz.get("cushion_name", "Cushion"))
            # Route to your existing drawing functions based on keys present
            try:
                if all(cz.get(k, 0) > 0 for k in ("length", "top_width", "bottom_width", "ear", "thickness")):
                    if cz.get("top_width") > cz.get("bottom_width"):
                        draw_t_shape(c, cz)
                    else:
                        draw_l_shape(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("diameter", "thickness")):
                    name = (cz.get("cushion_name") or "").lower()
                    if "semi" in name:
                        draw_semi_round(c, cz)
                    else:
                        draw_round(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("front_width_straight", "back_width_straight", "thickness", "front_width_curved", "back_width_curved")):
                    draw_curved_cushion(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("top_thickness", "bottom_thickness", "height", "length")):
                    draw_tapered_bolster(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("width", "side_length", "middle_length")):
                    draw_curved(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("side", "thickness")):
                    draw_equilateral_triangle(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("top_width", "bottom_width", "length")):
                    name = (cz.get("cushion_name") or "").lower()
                    if "left" in name:
                        draw_left_cushion(c, cz)
                    else:
                        draw_right_cushion(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("top_width", "bottom_width", "height", "edge")):
                    draw_clipped_trapeze(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("top_base", "bottom_base", "height")):
                    draw_trapezium(c, cz)
                elif all(cz.get(k, 0) > 0 for k in ("width", "length", "thickness")):
                    name = (cz.get("cushion_name") or "").lower()
                    if "triangle" in name:
                        draw_right_triangle(c, cz)
                    else:
                        draw_rectangle(c, cz)
                else:
                    raise ValueError("Unable to determine cushion shape. Missing key dimensions.")
            except Exception as inner_e:
                # draw error note on page to help debugging, but continue
                c.setFont("Helvetica", 10)
                c.setFillColorRGB(0.7, 0, 0)
                c.drawString(MARGIN_L, MARGIN_B, f"Draw error: {str(inner_e)}")
                c.setFillColorRGB(0, 0, 0)

            _page_footer(c)
            c.showPage()

        # Finish
        c.save()

        base = base_url.rstrip('/')
        pdf_link = f"{base}/pdfs/{filename}"
        JOBS[job_id].update(status="done", pdf_link=pdf_link)

    except Exception as e:
        JOBS[job_id].update(status="error", error=str(e))


# ---------------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------------

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

# ---- Sync fast-path: simple single cushion (rectangle or round) ----
@app.route('/generate-confirmation-sync', methods=['POST'])
def generate_confirmation_sync():
    data = request.get_json(force=True)
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

    filename = f"confirmation_{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(PDF_DIR, filename)
    c = _new_canvas(filepath)

    # Header + customer info
    _page_header(c, "ORDER CONFIRMATION (FAST)")
    y = PAGE_H - MARGIN_T - 0.35 * inch
    c.setFont("Helvetica", 11)
    for k, v in [("Customer", data["customer_name"]), ("Order", data["order_id"]), ("Email", data["email"])]:
        c.drawString(MARGIN_L, y, f"{k}: {v}")
        y -= 16
    _page_footer(c)
    c.showPage()

    # One cushion page
    if is_rect:
        draw_rectangle(c, cz)
    else:
        draw_round(c, cz)
    _page_footer(c)
    c.showPage()

    c.save()
    base = request.url_root.rstrip('/')
    return jsonify({"pdf_link": f"{base}/pdfs/{filename}", "mode": "sync"}), 200


# ---- Async flow (recommended for complex, multi-page jobs) ----
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


@app.route('/await/<job_id>', methods=['GET'])
def await_job(job_id):
    t0 = time.time()
    timeout_s = float(os.environ.get("AWAIT_TIMEOUT", "8"))
    while time.time() - t0 < timeout_s:
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
    return jsonify({"status": JOBS.get(job_id, {}).get("status", "queued")}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
