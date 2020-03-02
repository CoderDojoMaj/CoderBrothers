from flask import Flask, escape, request, redirect, send_from_directory

app = Flask(__name__)

@app.route('/', defaults={'page': 'index.html'})
@app.route('/<path:page>')
def page(page):
    print(f'Loading {page}')
    return send_from_directory(
            'web/',
            page)

app.run(host='0.0.0.0', port=8080)