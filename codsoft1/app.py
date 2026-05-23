# ULTRA ADVANCED AI HANDWRITTEN TEXT GENERATOR
# app.py

from flask import Flask, render_template, request
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageEnhance
)

import os
import random
from datetime import datetime

app = Flask(__name__)

GENERATED_FOLDER = "static/generated"

os.makedirs(GENERATED_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():

    text = request.form['text']

    style = request.form['style']

    bg_color = request.form['bgcolor']

    text_color = request.form['textcolor']

    paper = request.form['paper']

    shadow = request.form.get('shadow')

    noise = request.form.get('noise')

    width = 1600
    height = 700

    image = Image.new("RGB", (width, height), bg_color)

    draw = ImageDraw.Draw(image)

    # Paper texture simulation

    if paper == "lined":

        for i in range(0, height, 40):

            draw.line(
                (0, i, width, i),
                fill=(180, 180, 255),
                width=1
            )

    elif paper == "grid":

        for i in range(0, width, 40):

            draw.line(
                (i, 0, i, height),
                fill=(220, 220, 220),
                width=1
            )

        for j in range(0, height, 40):

            draw.line(
                (0, j, width, j),
                fill=(220, 220, 220),
                width=1
            )

    # Font styles

    if style == "normal":
        font_size = 58

    elif style == "bold":
        font_size = 72

    elif style == "thin":
        font_size = 48

    else:
        font_size = 60

    try:
        font = ImageFont.truetype("arial.ttf", font_size)

    except:
        font = ImageFont.load_default()

    x = 70
    y = 220

    # Multi-line support

    lines = text.split('\n')

    for line in lines:

        x = 70

        for char in line:

            offset_x = random.randint(-2, 2)

            offset_y = random.randint(-4, 4)

            angle = random.randint(-8, 8)

            temp = Image.new(
                "RGBA",
                (120, 120),
                (255, 255, 255, 0)
            )

            temp_draw = ImageDraw.Draw(temp)

            # Shadow effect

            if shadow:

                temp_draw.text(
                    (14, 14),
                    char,
                    font=font,
                    fill=(50, 50, 50)
                )

            temp_draw.text(
                (10, 10),
                char,
                font=font,
                fill=text_color
            )

            rotated = temp.rotate(angle, expand=1)

            image.paste(
                rotated,
                (x + offset_x, y + offset_y),
                rotated
            )

            x += 38

        y += 90

    # Noise effect

    if noise:

        pixels = image.load()

        for i in range(width):

            for j in range(height):

                if random.randint(1, 100) <= 2:

                    pixels[i, j] = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255)
                    )

    # Smooth effect

    image = image.filter(ImageFilter.SMOOTH_MORE)

    # Enhance sharpness

    enhancer = ImageEnhance.Sharpness(image)

    image = enhancer.enhance(1.3)

    filename = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"

    filepath = os.path.join(GENERATED_FOLDER, filename)

    image.save(filepath)

    return render_template(
        'index.html',
        generated_image=filepath
    )


if __name__ == '__main__':
    app.run(debug=True)