import click

from flask import Flask, escape, request, redirect, send_from_directory, abort, render_template
from flaskext.markdown import Markdown
import python.setup as setup
import python.crypto

from os import path


app = Flask(__name__)

# For developing. Disable chaching for non html files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

Markdown(app)

@app.before_first_request
def startup():
    setup.setup() # Load config before other modules

@app.route('/post/<path:page>')
def post(page):
    print(f'Loading post {page}')
    if(path.exists(f'templates/posts/{page}.md')):
        return render_template(f'posts/{page}.md')
    else:
        abort(404, f'post/{page}')




@app.route('/', defaults={'page': 'index.html'})
@app.route('/<path:page>')
def page(page):
    print(f'Loading {page}')
    return send_from_directory('web/', page)

@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='localhost', port=8080)