from flask import Flask, escape, request, redirect, send_from_directory

app = Flask(__name__)

# For developing. Disable chaching for non html files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', defaults={'page': 'index.html'})
@app.route('/<path:page>')
def page(page):
    print(f'Loading {page}')
    return send_from_directory('web/', page)

app.run(host='localhost', port=8080)