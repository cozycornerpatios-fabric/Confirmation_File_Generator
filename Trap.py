from flask import Flask, request, jsonify, send_from_directory, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black
import os
import uuid
import sys
import math

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-trapezoid-spec', methods=['GET', 'POST'])
def generate_trapezoid_spec():
    try:
        print("HEADERS:", dict(request.headers), file=sys.stderr)

        data = request.get_json(force=True) if request.method == 'POST' else request.args.to_dict()
        for key in data:
            if isinstance(data[key], str):
                data[key] = data[key].strip()

        required_fields = ['top_base', 'bottom_base', 'height', 'zipper', 'fill', 'fabric', 'piping', 'ties']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        top_base_in = float(data['top_base'])
        bottom_base_in = float(data['bottom_base'])
        height_in = float(data['height'])
        zipper_position = data['zipper']
        fill = data['fill']
        fabric = data['fabric']
        piping = data['piping']
        ties = data['ties']

        # === SCALING ===
        max_width = 5 * inch
        max_height = 4 * inch
        scale = min(max_width / bottom_base_in, max_height / height_in)

        top_base = top_base_in * scale
        bottom_base = bottom_base_in * scale
        height = height_in * scale
        half_diff = (bottom_base_in - top_base_in) / 2
        slant_len_in = round(math.sqrt(half_diff**2 + height_in**2), 2)

        # === COORDINATES ===
        x_origin = 1 * inch
        y_origin = 5.5 * inch
        top_left = (x_origin + (bottom_base - top_base) / 2, y_origin + height)
        top_right = (top_left[0] + top_base, top_left[1])
        bottom_left = (x_origin, y_origin)
        bottom_right = (x_origin + bottom_base, y_origin)
        center_top = ((top_left[0] + top_right[0]) / 2, top_left[1])
        center_bottom = ((bottom_left[0] + bottom_right[0]) / 2, bottom_left[1])

        # === PDF SETUP ===
        filename = f"trapezoid_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        # === TITLE ===
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, 10 * inch, "TRAPEZOID CUSHION SPEC")

        # === SPECS ===
        c.setFont("Helvetica", 10)
        specs = [
            f"Top Base: {top_base_in}\"",
            f"Bottom Base: {bottom_base_in}\"",
            f"Height: {height_in}\"",
            f"Slant Length: {slant_len_in}\"",
            f"Zipper: {zipper_position}",
            f"Fill: {fill}",
            f"Fabric: {fabric}",
            f"Piping: {piping}",
            f"Ties: {ties}"
        ]
        y = 9.5 * inch
        for line in specs:
            c.drawString(1 * inch, y, line)
            y -= 0.3 * inch

        # === DRAW SHAPE ===
        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.lines([
            (top_left[0], top_left[1], top_right[0], top_right[1]),
            (top_right[0], top_right[1], bottom_right[0], bottom_right[1]),
            (bottom_right[0], bottom_right[1], bottom_left[0], bottom_left[1]),
            (bottom_left[0], bottom_left[1], top_left[0], top_left[1])
        ])

        # === CENTER HEIGHT (dotted) ===
        c.setDash(3, 3)
        c.line(center_top[0], center_top[1], center_bottom[0], center_bottom[1])
        c.setDash()

        # === ZIPPER ===
        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.setFillColor(red)
        offset = 6
        if zipper_position == "Top":
            c.line(top_left[0], top_left[1] + 3, top_right[0], top_right[1] + 3)
            c.drawCentredString((top_left[0] + top_right[0]) / 2 + 100, top_left[1] + 8, "Zipper")
        elif zipper_position == "Bottom":
            c.line(bottom_left[0], bottom_left[1] - 3, bottom_right[0], bottom_right[1] - 3)
            c.drawCentredString(bottom_right[0] + 20, bottom_left[1] - 10, "Zipper")
        elif zipper_position == "Left":
            c.line(bottom_left[0] - offset, bottom_left[1], top_left[0] - offset, top_left[1])
            c.drawString(top_left[0] - offset - 10, (top_left[1] + bottom_left[1]) / 2 + 4, "Zipper")
        elif zipper_position == "Right":
            c.line(bottom_right[0] + offset, bottom_right[1], top_right[0] + offset, top_right[1])
            c.drawString(top_right[0] + offset + 3, top_right[1] + 5, "Zipper")

        # === LABELS ===
        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString((top_left[0] + top_right[0]) / 2 - 10, top_left[1] + 12, f"{top_base_in}\"")
        c.drawString((bottom_left[0] + bottom_right[0]) / 2 - 10, bottom_left[1] - 18, f"{bottom_base_in}\"")
        c.drawString(center_top[0] - 25, (center_top[1] + center_bottom[1]) / 2 - 5, f"{height_in}\"")
        c.drawString(bottom_left[0] - 10, (top_left[1] + bottom_left[1]) / 2 - 5, f"{slant_len_in}\"")
        c.drawString(bottom_right[0] - 25, (top_right[1] + bottom_right[1]) / 2 - 5, f"{slant_len_in}\"")

        c.save()

        return jsonify({
            "pdf_link": url_for('serve_pdf', filename=filename, _external=True)
        })

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10002))
    app.run(debug=True, host='0.0.0.0', port=port)

