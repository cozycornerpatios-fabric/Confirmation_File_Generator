from flask import Flask, request, jsonify, send_from_directory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black
import os
import uuid
import sys

app = Flask(__name__)
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-confirmation', methods=['GET', 'POST'])
def generate_confirmation():
    try:
        print("HEADERS:", dict(request.headers), file=sys.stderr)

        # Accept both GET and POST data
        data = request.get_json(force=True) if request.method == 'POST' else request.args.to_dict()

        # Strip whitespace
        for key in data:
            if isinstance(data[key], str):
                data[key] = data[key].strip()

        required_fields = ['length', 'width', 'thickness', 'fill', 'fabric', 'zipper', 'piping', 'ties']
        missing = [field for field in required_fields if field not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        length_in = int(data['length'])
        width_in = int(data['width'])
        thickness = int(data['thickness'])
        fill = data['fill']
        fabric = data['fabric']
        zipper_on = data['zipper']
        piping = data['piping']
        ties = data['ties']

        if zipper_on not in ["Short Side", "Long Side"]:
            return jsonify({"error": "Invalid 'zipper' value. Must be 'Short Side' or 'Long Side'"}), 400

        is_zipper_on_long = zipper_on == "Long Side"
        horizontal_side_in = max(length_in, width_in) if is_zipper_on_long else min(length_in, width_in)
        vertical_side_in = min(length_in, width_in) if is_zipper_on_long else max(length_in, width_in)

        max_draw_height = 4.25 * inch
        max_draw_width = 3.5 * inch
        scale_factor = min(max_draw_width / horizontal_side_in, max_draw_height / vertical_side_in)
        horizontal_side = horizontal_side_in * scale_factor
        vertical_side = vertical_side_in * scale_factor

        filename = f"confirmation_{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(PDF_DIR, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, "CONFIRMATION")

        specs = [
            "Shape: Rectangle",
            f"Length: {length_in} inches",
            f"Width: {width_in} inches",
            f"Thickness: {thickness} inches",
            f"Fill: {fill}",
            f"Fabric: {fabric}",
            f"Zipper Position: {zipper_on}",
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
        c.rect(x_origin, y_origin, horizontal_side, vertical_side)

        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(x_origin + horizontal_side / 2 - 0.15 * inch, y_origin - 0.3 * inch, f"{horizontal_side_in}\"")
        c.drawString(x_origin + horizontal_side + 0.1 * inch, y_origin + vertical_side / 2, f"{vertical_side_in}\"")

        c.setStrokeColor(red)
        c.setLineWidth(2)
        c.line(x_origin, y_origin + vertical_side, x_origin + horizontal_side, y_origin + vertical_side)
        c.setFillColor(red)
        c.drawString(x_origin + horizontal_side / 2 - 0.2 * inch, y_origin + vertical_side + 0.1 * inch, "Zipper")

        c.save()

        return jsonify({
            "pdf_link": f"{request.url_root}pdfs/{filename}"
        })

    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        return jsonify({"error": str(e)}), 500

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_DIR, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
