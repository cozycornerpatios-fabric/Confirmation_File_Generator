from flask import Flask, request, jsonify, send_from_directory, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black
import os
import uuid
import sys

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-clipped-trapezium', methods=['GET', 'POST'])
def generate_clipped_trapezium():
    try:
        print("HEADERS:", dict(request.headers), file=sys.stderr)

        data = request.get_json(force=True) if request.method == 'POST' else request.args.to_dict()
        for key in data:
            if isinstance(data[key], str):
                data[key] = data[key].strip()

        required_fields = ['bottom_width', 'top_width', 'height_in', 'edge', 'fill', 'fabric', 'zipper', 'piping', 'ties']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        bottom_width = float(data['bottom_width'])
        top_width = float(data['top_width'])
        height_in = float(data['height_in'])
        edge = float(data['edge'])
        fill = data['fill']
        fabric = data['fabric']
        zipper = data['zipper']
        piping = data['piping']
        ties = data['ties']

        offset = (bottom_width - top_width) / 2
        max_draw_height = 4.25 * inch
        max_draw_width = 3.5 * inch
        scale_factor = min(max_draw_width / bottom_width, max_draw_height / height_in)

        b = bottom_width * scale_factor
        t = top_width * scale_factor
        h = height_in * scale_factor
        e = edge * scale_factor
        o = offset * scale_factor

        verts = [
            (0, 0),
            (b, 0),
            (b, e),
            (o + t, h),
            (o, h),
            (0, e)
        ]

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "CONFIRMATION - CLIPPED TRAPEZOID")

        specs = [
            "Shape: Clipped Trapezoid",
            f"Bottom Width: {bottom_width} inches",
            f"Top Width: {top_width} inches",
            f"Height: {height_in} inches",
            f"Clipping Edge: {edge} inches",
            f"Fill: {fill}",
            f"Fabric: {fabric}",
            f"Zipper: {zipper}",
            f"Piping: {piping}",
            f"Ties: {ties}"
        ]

        y = height - 1.5 * inch
        for line in specs:
            c.drawString(1 * inch, y, line)
            y -= 0.3 * inch

        x_origin = 4.5 * inch
        y_origin = height - 6.5 * inch
        c.setStrokeColor(black)
        c.setLineWidth(1)
        path = c.beginPath()
        path.moveTo(x_origin + verts[0][0], y_origin + verts[0][1])
        for x, y_ in verts[1:]:
            path.lineTo(x_origin + x, y_origin + y_)
        path.close()
        c.drawPath(path)

        # Dimension labels
        angled_length = round(((edge**2 + ((bottom_width - top_width) / 2)**2)**0.5, 2)
        c.setFont("Helvetica", 8)
        c.drawString(x_origin + b / 2 - 14, y_origin + 4, f"{bottom_width}")
        c.drawString(x_origin + o + t / 2 - 14, y_origin + h - 9, f"{top_width}")
        c.drawString(x_origin - 10, y_origin + e + (h - e) / 2, f"{angled_length}")
        c.drawString(x_origin + b - 10, y_origin + e + (h - e) / 2, f"{angled_length}")

        # Height dotted line
        c.setDash(1, 2)
        center_x = x_origin + o + t / 2
        c.line(center_x, y_origin, center_x, y_origin + h)
        c.setDash()
        c.drawString(center_x + 5, y_origin + h / 2, f"{height_in}")

        # Zipper path
        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.setFillColor(red)
        x1, y1 = verts[0][0], verts[0][1] - 0.1 * inch
        x2, y2 = verts[1][0], verts[1][1] - 0.1 * inch
        c.line(x_origin + x1, y_origin + y1, x_origin + x2, y_origin + y2)
        c.drawString(x_origin + (x1 + x2) / 2, y_origin + y1 - 0.1 * inch, "Zipper")

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
    port = int(os.environ.get("PORT", 10001))
    app.run(debug=True, host='0.0.0.0', port=port)
