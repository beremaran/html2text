import os
import hashlib
from docx import Document

import requests
import html2text
import md_to_doc
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
STATIC_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/convert', methods=['POST'])
def convert_urls():
    result = {}

    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True

    renderer = md_to_doc.PythonDocxRenderer()

    urls = str(request.form['urls']).splitlines()
    print(request.form['urls'])

    for url in urls:
        print(url)
        r = requests.get(url).text
        md = str(h.handle(r)).replace('\r', '\\r').replace('\n', '\\n').replace('"', '\\"')
        document = Document()
        exec(md_to_doc.MarkdownWithMath(renderer=renderer)(md))
        doc_file = hashlib.md5(url.encode('ascii')).hexdigest() + '.docx'
        doc_path = os.path.join(STATIC_DIR, doc_file)
        document.save(doc_path)
        result[url] = doc_file

    return jsonify({
        'status': True,
        'data': result
    })


if __name__ == '__main__':
    app.run(host= '0.0.0.0')
