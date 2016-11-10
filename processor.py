import json
import sys

import pyocr
import pyocr.builders
from flask import Flask, render_template, request
from Levenshtein import _levenshtein
from PIL import Image, ImageEnhance

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)

        # The tools are returned in the recommended order of usage
        tool = tools[0]

        image_obj = Image.open(request.files['image'])

        image_obj = ImageEnhance.Color(image_obj).enhance(0)
        image_obj = ImageEnhance.Sharpness(image_obj).enhance(2)
        image_obj = ImageEnhance.Contrast(image_obj).enhance(2)

        txt = tool.image_to_string(
            image_obj,
            lang='eng',
            builder=pyocr.builders.TextBuilder()
        )

        if not txt:
            return render_template('results.html')

        txt = " ".join(txt.split())

        cards = []

        with open('data/black.json') as f:
            cards.extend(json.load(f))

        with open('data/white.json') as f:
            cards.extend(json.load(f))

        distances = []

        for card in cards:
            distances.append([_levenshtein.distance(txt, card), card])

        distances.sort(key=lambda tup: tup[0])
        return render_template(
            'results.html',
            cards=distances,
            detected=txt,
            image=image_obj
        )

    return render_template('index.html')
