from flask import Flask, request, jsonify, send_from_directory, url_for
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black, blue
import os
import uuid
import sys

app = Flask(__name__)
PDF_DIR = os.path.join(os.getcwd(), "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/generate-confirmation', methods=['GET', 'POST'])
def generate_confirmation():
    try:
        print("HEADERS:", dict(request.headers), file=sys.stderr)

        data = request.get_json(force=True) if request.method == 'POST' else request.args.to_dict()
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

        piping_margin = 0.1 * inch if piping.lower() == "yes" else 0
        diagram_total_height = vertical_side + (0.2 * inch if piping.lower() == "yes" else 0)
        x_origin = (width - horizontal_side) / 2
        y_origin = y - diagram_total_height - 0.5 * inch

        c.setStrokeColor(black)
        c.setLineWidth(1)
        c.rect(x_origin, y_origin, horizontal_side, vertical_side)

        if piping.lower() == "yes":
            c.setStrokeColor(blue)
            c.setLineWidth(1)
            c.rect(
                x_origin - piping_margin,
                y_origin - piping_margin,
                horizontal_side + 2 * piping_margin,
                vertical_side + 2 * piping_margin
            )
            c.setFillColor(blue)
            c.setFont("Helvetica", 10)
            c.drawString(
                x_origin + horizontal_side + piping_margin + 0.1 * inch + 6,
                y_origin + vertical_side + piping_margin - 0.15 * inch,
                "Piping"
            )

        c.setFont("Helvetica", 10)
        c.setFillColor(black)
        c.drawString(x_origin + horizontal_side / 2 - 0.15 * inch, y_origin - 0.3 * inch - 10, f"{horizontal_side_in}\"")
        c.drawString(x_origin + horizontal_side + 0.1 * inch + 6, y_origin + vertical_side / 2, f"{vertical_side_in}\"")

        c.setStrokeColor(red)
        c.setLineWidth(2)
        zipper_y = y_origin + vertical_side + 0.1 * inch
        c.line(x_origin, zipper_y, x_origin + horizontal_side, zipper_y)
        c.setFillColor(red)
        c.drawString(x_origin + horizontal_side / 2 - 0.2 * inch, zipper_y + 0.1 * inch + 10, "Zipper")

        # Draw ties
        c.setStrokeColor(black)
        c.setLineWidth(1)
        tie_len = 0.2 * inch
        tie_offset_in = 4
        tie_offset = tie_offset_in * scale_factor

        def draw_tie(x, y, direction, orientation='horizontal'):
            if orientation == 'horizontal':
                if direction == 'left':
                    c.line(x, y, x - tie_len, y - tie_len)
                    c.line(x, y, x - tie_len, y + tie_len)
                elif direction == 'right':
                    c.line(x, y, x + tie_len, y - tie_len)
                    c.line(x, y, x + tie_len, y + tie_len)
            elif orientation == 'vertical':
                if direction == 'down':
                    c.line(x, y, x - tie_len, y - tie_len)
                    c.line(x, y, x + tie_len, y - tie_len)
                elif direction == 'up':
                    c.line(x, y, x - tie_len, y + tie_len)
                    c.line(x, y, x + tie_len, y + tie_len)

        if ties.lower() != "none":
            short_side_is_vertical = vertical_side < horizontal_side
            xo = x_origin - piping_margin
            yo = y_origin - piping_margin
            hs = horizontal_side + 2 * piping_margin
            vs = vertical_side + 2 * piping_margin

            if short_side_is_vertical:
                left_x = xo
                right_x = xo + hs
                y_top = yo
                y_bot = yo + vs

                if ties == "2 Side":
                    draw_tie(left_x, yo + vs / 2, 'left', 'horizontal')
                    draw_tie(right_x, yo + vs / 2, 'right', 'horizontal')
                elif ties == "4 Corner":
                    draw_tie(left_x, y_top, 'left', 'horizontal')
                    draw_tie(left_x, y_bot, 'left', 'horizontal')
                    draw_tie(right_x, y_top, 'right', 'horizontal')
                    draw_tie(right_x, y_bot, 'right', 'horizontal')
                elif ties == "4 Side":
                    draw_tie(left_x, y_top + tie_offset, 'left', 'horizontal')
                    draw_tie(left_x, y_bot - tie_offset, 'left', 'horizontal')
                    draw_tie(right_x, y_top + tie_offset, 'right', 'horizontal')
                    draw_tie(right_x, y_bot - tie_offset, 'right', 'horizontal')
            else:
                top_y = yo
                bottom_y = yo + vs
                x_left = xo
                x_right = xo + hs

                if ties == "2 Side":
                    draw_tie(xo + hs / 2, top_y, 'down', 'vertical')
                    draw_tie(xo + hs / 2, bottom_y, 'up', 'vertical')
                elif ties == "4 Corner":
                    draw_tie(x_left, top_y, 'down', 'vertical')
                    draw_tie(x_left, bottom_y, 'up', 'vertical')
                    draw_tie(x_right, top_y, 'down', 'vertical')
                    draw_tie(x_right, bottom_y, 'up', 'vertical')
                elif ties == "4 Side":
                    draw_tie(x_left + tie_offset, top_y, 'down', 'vertical')
                    draw_tie(x_right - tie_offset, top_y, 'down', 'vertical')
                    draw_tie(x_left + tie_offset, bottom_y, 'up', 'vertical')
                    draw_tie(x_right - tie_offset, bottom_y, 'up', 'vertical')

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
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)

