# Remove for prod
# check for dependencies

try:
	import click
	from flask import Flask, escape, request, redirect, send_from_directory, abort, render_template, render_template_string, make_response, session, send_file
	from flaskext.markdown import Markdown
	from python import blog as b
	from python import logger as liblogger
	from python import crypto
	from python import scsscompiler
	from python.db import PostNotFoundError, getDB, UserNotFoundError, UserDuplicateError
	from python.setup import setup, get_config, get_pub_key, get_priv_key
	from python.decorators import login_required
	from os import path, environ
	import base64, io, rsa, time, os, json
except ImportError as e:
	import sys
	print('\n'*10)
	print('#'*30)
	print(f'{e.name} missing!!! (Dependency)')
	print('Please install dependencies using')
	print(f'    python{sys.version_info[0]}.{sys.version_info[1]} -m pip install -r requirements.txt         # See README.md for more options')
	print('#'*30)
	exit(1)

app = Flask('CoderBrothers')
app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
# app.config['SESSION_COOKIE_SECURE'] = True

logger = liblogger.get('server')
if __name__ == "__main__":
	logger.warning('PLEASE use flask run and do not run this file (do not do python3 server.py)')
	logger.warning('Setting env to development, but not starting debugger (autoreload)')
	app.env = 'development'

if app.env == 'development' and not app.debug:
	# For developing. Disable chaching for non html files
	app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

if environ.get("WERKZEUG_RUN_MAIN") == "true":
	setup() # Run this here so that config errors can be seen (don't run in prod)

Markdown(app)

@app.before_first_request
def startup():
	app.secret_key = get_config()['key'] # If setup hasn't been called, this will call it

@app.route('/pubkey')
def pubkey():
	pub_key = get_pub_key()
	return ','.join([hex(pub_key.n), hex(pub_key.e)])

# @app.route('/decrypt', methods=['POST']) # test endpoint
# def decrypt():
# 	decr = crypto.decrypt_RSA_from_sendable_bytes(request.data).decode('utf8')
# 	print(decr)
# 	return ('', 200)

@app.route('/post/<uuid>')
def post(uuid):
	logger.info(f'Loading post {uuid}')
	try:
		useruuid = None
		if session.get('user'):
			useruuid = session.get('user')[1]
		res = make_response(render_template_string(b.getPostTemplate(uuid), post_uuid = uuid, comments = getDB().getComments(uuid, useruuid)))
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

@app.route('/post/<post_uuid>/reply/<comment_uuid>', methods=['POST'])
@login_required
def reply(user_uuid, post_uuid, comment_uuid):
	logger.info(f'Replying {comment_uuid}')
	try:
		getDB().postComment(post_uuid, user_uuid, request.form['content'], replyTo=comment_uuid)
		return redirect(f'/post/{post_uuid}')
	except PostNotFoundError:
		abort(404, f'post/{post_uuid}')

@app.route('/post/<post_uuid>/vote/<comment_uuid>', methods=['POST'])
@login_required
def vote(user_uuid, post_uuid, comment_uuid):
	logger.info(f'Replying {comment_uuid}')
	try:
		logger.info('VOTING '+request.form['vote'])
		getDB().vote(user_uuid, comment_uuid, request.form['vote'])
		return redirect(f'/post/{post_uuid}')
	except PostNotFoundError:
		abort(404, f'post/{post_uuid}')
	except:
		abort(500, 'Error voting')

@app.route('/post/<post_uuid>/add_file', methods = ['GET'])
@login_required(perms_level=1)
def add_file_to_post_GET(user_uuid, post_uuid):
	return render_template('add_file.html', post_uuid = post_uuid)

@app.route('/post/<post_uuid>/add_file', methods = ['POST'])
@login_required(perms_level=1)
def add_file_to_post(user_uuid, post_uuid):
	if 'file' in request.files:
		f = request.files['file']
		print(f.filename)
		if not os.path.isdir(f'web/post/{post_uuid}'):
			os.mkdir(f'web/post/{post_uuid}')
		f.save(os.path.join(f'web/post/{post_uuid}', f.filename))
	return 'ok'

@app.route('/post/<uuid>/file/<file>', methods = ['GET'])
def load_file_for_post(uuid, file):
	if os.path.isdir(f'web/post/{uuid}'):
		if os.path.isfile(f'web/post/{uuid}/{file}'):
			return send_file(f'web/post/{uuid}/{file}')
		else:
			return abort(404, 'File not found')
	else:
		return abort(404, 'Post files not found')

@app.route('/post/<post_uuid>/edit', methods = ['GET'])
@login_required(perms_level=1)
def edit_post_page(_, post_uuid):
	logger.info(f'Loading post {post_uuid}')
	try:
		post = getDB().getPost(post_uuid)
		return render_template('create_post.html', title = post['title'], content = post['content'], editPost = post_uuid)
	except PostNotFoundError:
		abort(404, f'/post/{post_uuid}/edit')

@app.route('/post/<post_uuid>/edit', methods = ['POST'])
@login_required(perms_level=1)
def edit_post(_, post_uuid):
	getDB().editPost(post_uuid, request.form['title'], request.form['content'])
	return redirect('/post/' + post_uuid)

@app.route('/post/<post_uuid>/delete', methods = ['POST'])
@login_required(perms_level=1)
def delete_post(_, post_uuid):
	getDB().deletePost(post_uuid)
	return redirect('/blog')


@app.route('/blog')
def blog():
	return render_template('blog.html', posts=b.get_posts())

@app.route('/posts')
def posts():
	page = request.args.get('page')
	postsPerPage = request.args.get('posts_per_page')
	search = request.args.get('search')
	if page is None:
		return abort(400, 'page field in get request isn\'t present')
	if postsPerPage is None:
		return abort(400, 'posts_per_page field in get request isn\'t present')
	posts = None
	if search is None:
		posts = b.get_posts_paged(int(page), int(postsPerPage))
	else:
		posts = b.search_posts_paged(search, int(page), int(postsPerPage))
	return render_template('posts.html', posts=posts)

@app.route('/create_post', methods = ['GET'])
@login_required(perms_level=1)
def create_post_GET(uuid):
	# session['user'] = getDB().getUserFromUUID(uuid)
	return render_template('create_post.html')

@app.route('/create_post', methods = ['POST'])
@login_required(perms_level=1)
def create_post_POST(uuid):
	post_uuid = getDB().createPost(request.form['title'], uuid, request.form['content'])
	return redirect('/post/' + post_uuid)

@app.route('/login', methods = ['POST'])
def login():
	data = json.loads(crypto.decrypt_RSA_from_sendable_bytes(request.data).decode('utf8'))
	try:
		if getDB().checkPassword(data['username'], data['password']):
			user_uuid = getDB().getUserUUID(data['username'])
			session['user'] = (getDB().addSession(user_uuid), user_uuid, getDB().getUserFromUUID(user_uuid)[0], getDB().getUserPerms(user_uuid))
			return json.dumps({"ok": True})
		else:
			return json.dumps({"error": "Invalid credentials"})
	except UserNotFoundError:
		return json.dumps({"error": "User not found"})

@app.route('/signup', methods = ['POST'])
def signup():
	data = json.loads(crypto.decrypt_RSA_from_sendable_bytes(request.data).decode('utf8'))
	try:
		getDB().addUser(data['username'], data['password'], 0)
		user_uuid = getDB().getUserUUID(data['username'])
		session['user'] = (getDB().addSession(user_uuid), user_uuid, getDB().getUserFromUUID(user_uuid)[0], getDB().getUserPerms(user_uuid))
		return json.dumps({"ok": True})
	except UserDuplicateError:
		return json.dumps({"error": "Username not available"})
	

@app.route('/logout')
def logout():
	getDB().deleteSession(session['user'][0])
	session['user'] = None
	return redirect('/blog')

@app.route('/img')
def img():
	return render_template('image.html')

@app.route('/update_img', methods=['POST'])
@login_required
def update_img(uuid):
	getDB().setUserImage(uuid, request.form['image'])
	return redirect('/img')

@app.route('/u/<uuid>/img')
def u_img(uuid):
	img = getDB().getUserImage(uuid)
	response = send_file(io.BytesIO(bytes(img)), mimetype='image/png')
	response.headers.add_header('Cache-Control','no-cache')
	return response

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/css/<path:file>')
def css(file):
	scsscompiler.compile(file)
	logger.info(f'Loading css {file}')
	response = send_from_directory('web/css/', file)
	response.headers.add_header('Cache-Control','no-cache')
	return response

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
	app.run(host='localhost', port=8080) #Quitar el modo debug cuando en producción