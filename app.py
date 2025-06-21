from flask import Flask, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import red, black
import io

app = Flask(__name__)

@app.route('/generate-confirmation', methods=['POST'])
def generate_confirmation():
    data = request.json
    length_in = data['length']
    width_in = data['width']
    thickness = data['thickness']
    fill = data['fill']
    fabric = data['fabric']
    zipper_on = data['zipper']
    piping = data['piping']
    ties = data['ties']

    is_zipper_on_long = zipper_on == "Long Side"
    if is_zipper_on_long:
        horizontal_side_in = max(length_in, width_in)
        vertical_side_in = min(length_in, width_in)
    else:
        horizontal_side_in = min(length_in, width_in)
        vertical_side_in = max(length_in, width_in)

    max_draw_height = 4.25 * inch
    max_draw_width = 3.5 * inch
    scale_factor = min(max_draw_width / horizontal_side_in, max_draw_height / vertical_side_in)
    horizontal_side = horizontal_side_in * scale_factor
    vertical_side = vertical_side_in * scale_factor

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
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
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="confirmation.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

