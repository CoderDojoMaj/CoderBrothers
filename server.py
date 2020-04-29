import click
from flask import Flask, escape, request, redirect, send_from_directory, abort, render_template, render_template_string, make_response
from flaskext.markdown import Markdown
from python import blog as b
from python import logger as liblogger
from python.db import PostNotFoundError, getDB
from python.setup import get_config
from os import path

app = Flask('CoderBrothers')
logger = liblogger.get('server')

# For developing. Disable chaching for non html files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


app.secret_key = get_config()['key']

Markdown(app)

@app.before_first_request
def startup():
    pass

@app.route('/post/<uuid>')
def post(uuid):
    logger.info(f'Loading post {uuid}')
    try:
        res = make_response(render_template_string(b.getPostTemplate(uuid)))
        res.set_cookie('id', '1')
        return res
    except PostNotFoundError:
        abort(404, f'post/{uuid}')

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=b.get_posts())

@app.route('/create_post', methods = ['GET'])
def create_post_GET():
    return render_template('create_post.html')

@app.route('/create_post', methods = ['POST'])
def create_post_POST():
    getDB().createPost(request.form['title'], request.form['author'], request.form['content'])
    #984e0b91-8a17-11ea-8b30-7085c2f88ddd
    return redirect('/create_post')

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