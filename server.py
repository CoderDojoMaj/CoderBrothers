import click
from flask import Flask, escape, request, redirect, send_from_directory, abort, render_template
from flaskext.markdown import Markdown
from python import setup
from python import blog as b
from python import logger as liblogger
from python.db import DB
from os import path

setup.setup() # Load config before other modules

app = Flask('CoderBrothers')
app.logger
logger = liblogger.get('server')

# For developing. Disable chaching for non html files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

Markdown(app)

db = None

@app.before_first_request
def startup():
    pass

@app.route('/post/<path:page>')
def post(page):
    logger.info(f'Loading post {page}')
    if(path.exists(f'templates/posts/{page}.md')):
        return render_template(f'posts/{page}.md')
    else:
        abort(404, f'post/{page}')

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=b.get_posts())

@app.route('/', defaults={'page': 'index.html'})
@app.route('/<path:page>')
def page(page):
    logger.info(f'Loading {page}')
    return send_from_directory('web/', page)

@app.errorhandler(404)
def page_not_found(error):
    logger.error(error)
    return render_template('404.html'), 404

@app.context_processor
def utility_functions():
    log = liblogger.get('TEMPLATE')
    def printconsole(message):
        log.info(str(message))

    return dict(console=printconsole)

if __name__ == "__main__":
    app.run(host='localhost', port=8080)