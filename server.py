from flask import Flask, escape, request, redirect

app = Flask(__name__)

@app.route('/')
def hello():
    return redirect('/index.html')

@app.route('/<page>')
def page(page):
    print(f'Loading {page}')
    return open('web/'+page).read()

app.run(host='0.0.0.0', port=8080)