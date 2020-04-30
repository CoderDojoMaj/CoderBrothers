import click
from flask import Flask, escape, request, redirect, send_from_directory, abort, render_template, render_template_string, make_response, session
from flaskext.markdown import Markdown
from python import blog as b
from python import logger as liblogger
from python.db import PostNotFoundError, getDB, UserNotFoundError, UserDuplicateError
from python.setup import setup, get_config
from python.decorators import login_required
from os import path, environ

app = Flask('CoderBrothers')

logger = liblogger.get('server')
if __name__ == "__main__":
    logger.warning('PLEASE use flask run and do not run this file (do not do python3 server.py)')
    logger.warning('Setting env to development, but not starting debugger (autoreload)')
    app.env = 'development'

if app.env == 'development' and (not app.debug or environ.get("WERKZEUG_RUN_MAIN") == "true"):
    setup() # Run this here so that config errors can be seen (don't run in prod)
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
        res = make_response(render_template_string(b.getPostTemplate(uuid), post_uuid = uuid, comments = getDB().getComments(uuid)))
        return res
    except PostNotFoundError:
        abort(404, f'post/{uuid}')

@app.route('/post/<uuid>/comment', methods=['POST'])
@login_required
def comment(user_uuid, uuid):
    logger.info(f'Commenting {uuid}')
    try:
        getDB().postComment(uuid, user_uuid, request.form['content'])
        return redirect(f'/post/{uuid}')
    except PostNotFoundError:
        abort(404, f'post/{uuid}')

@app.route('/blog')
def blog():
    return render_template('blog.html', posts=b.get_posts())

@app.route('/create_post', methods = ['GET'])
@login_required(perms_level=1)
def create_post_GET(uuid):
    # session['user'] = getDB().getUserFromUUID(uuid)
    return render_template('create_post.html')

@app.route('/create_post', methods = ['POST'])
@login_required(perms_level=1)
def create_post_POST(uuid):
    getDB().createPost(request.form['title'], uuid, request.form['content'])
    return redirect('/create_post')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            if getDB().checkPassword(request.form['username'], request.form['password']):
                user_uuid = getDB().getUserUUID(request.form['username'])
                session['user'] = (getDB().addSession(user_uuid), user_uuid, getDB().getUserFromUUID(user_uuid)[0])
                return redirect('/blog')
            else:
                return render_template('login.html', error='Invalid credentials')
        except UserNotFoundError:
            return render_template('login.html', error='User not found')
    else:
        return render_template('login.html')

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            getDB().addUser(request.form['username'], request.form['password'], 0)
            user_uuid = getDB().getUserUUID(request.form['username'])
            session['user'] = (getDB().addSession(user_uuid), user_uuid, getDB().getUserFromUUID(user_uuid)[0])
            return redirect('/blog')
        except UserDuplicateError:
            return render_template('signup.html', error='Username not available')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    getDB().deleteSession(session['user'][0])
    session['user'] = None
    return 'Done'

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