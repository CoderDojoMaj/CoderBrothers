from mysql import connector as mysql
from mysql.connector import errorcode as mysql_errorcode
from python import setup, logger, crypto, utils
import atexit
import uuid as libUUID
import base64
from math import ceil
DEFAULT_IMAGE = base64.b64decode('/9j/4AAQSkZJRgABAQEASABIAAD//gA7Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2NjIpLCBxdWFsaXR5ID0gOTAK/9sAQwAEAgMDAwIEAwMDBAQEBAUJBgUFBQULCAgGCQ0LDQ0NCwwMDhAUEQ4PEw8MDBIYEhMVFhcXFw4RGRsZFhoUFhcW/8AACwgAgACAAQERAP/EABwAAQACAwEBAQAAAAAAAAAAAAAGBwMEBQIBCP/EADgQAAICAQICBwQJAwUAAAAAAAABAgMEBREGIQcSEzFBUWFxgZGhFBUiMlKxweHwIzOyQmOCktH/2gAIAQEAAD8A/RQAAAAAAAAAAAAAAAAAAAAAAAAABkxaLsjIhRRXKy2x9WMYrdtk74a4Foqgr9Xfa2Nb9hCW0I+1rm37OXtJZhYGFhxUcbEopS/BWonrMw8TKj1cnFpuT8LK1L8yLcR8C4eRB3aVL6Nd39lJt1y/Vfl6EBzsa/Dyp4+TXKu2t7Si/AwgAAAAs7o84fhpmnrMyIL6Zet3uudUX3RXr5/DwJMACP8AHOg16xp0p1QSzKYt1S8ZL8D9H4eT95Vkk4ycZJxaezT70fAAAAdfgbBjn8T41M1vXCXaT9VHnt73sveW6AACqukvAjhcU2uEdoZMVckvN7qXzTfvOAAAACV9ECT4nu3S3WJLb/vAskAAFe9MiX1phPbn2Muf/IhoAAAO70cZccTi7H672jf1qm/Vrl80i1wAAVf0qZayeKpVRe6xao1vbz5yf+W3uI2AAAD1XOULIzhJxlFpxku9PzLc4R1erWdIryOsu2glG+K/0z/8fev2OsADncSanRpGl2ZlzTcVtXDfnOXgv54blQZV1mTk2ZF0utZbNynLzbe7MYAAAB0eGdSz9N1KNmApWTn9mVKTkrV5NItfSMi3LwoX3YluLOX3qrdusv2+HsNwGvqWRPFw53wxrciUVyqrScpFUcW6rqGqalKWdCVKr3UMdppVr2Px82coAAAA7/CHC2XrUlfY3Rhp87Guc/SK/Xu9pYui6Rp+lUKvCxlB7bSm1vKXtf8AEdAAGhrOk6fqtHZZuNCzZfZl3Tj7Jd6K74w4VytHbyKW78Pf+5t9qv0kv1/IjwAABIuAOHXrGY8jJTWHRJdf/cl+Ffr+5Z1VcKq1XXFRhBJRilskl4IyAAAx21wtrddkVKE01KMlumn4MrLpA4c+qMpZWLFvDulsl39lL8L9PL+bxwAA2NKw7tQ1GnCoW9l01Fb9y82/RLd+4uHSMKjTtOqwseO1dUeqn4t+Lfq3zNsAAAGrquHTn4FuHfFOu6PVfmvJr1T5lPaxhW6dqd+Ff9+mbjvt95eD962ZrAAm3Q/p6nfk6nOO6r/o1P1fOXy2+LJ8AAAACB9MGnJSxtUrjt1v6NrXxi/8vkQcAFs9HmKsXhLEW2zti7ZPz6z3Xy2O2AAAADi8e4v0zhPMhtzrr7WL8nH7T+Sa95UoALr0mpU6VjUpbKumEfhFI2QAAAAYNQgrsG+p81OqUfimikgf/9k=')

POSTS_PER_PAGE = 10

db = None
db_started = False


def getDB():  # Only get a single DB object (singleton)
	global db
	global db_started

	if db is None or db_started == False:
		db_started = True
		db = DB()
	return db


class DB:
	def __init__(self):
		config = setup.get_config()['db']
		self.l = logger.get('DB')
		self.connection = None
		try:
			self.connection = mysql.connect(
				user=config['user'], password=config['password'], database='coderbrothers', autocommit=True)
			self.l.info('Connection started')
		except mysql.Error as err:
			if err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
				self.l.critical(
					"Something is wrong with your user name or password")
			elif err.errno == mysql.errorcode.ER_BAD_DB_ERROR:
				self.l.critical("Database does not exist")
			else:
				self.l.critical(err)
			exit(1)

		if self.connection is None:
			self.l.critical('Couldn\'t connect to the database')
			exit(1)

		atexit.register(self.close)

	def run(self, comm, *args, raw=False):
		cursor = None
		try:
			cursor = self.connection.cursor(raw=raw)
		except mysql.errors.OperationalError:
			self.l.warning('Reconnecting')
			self.connection.reconnect()
			cursor = self.connection.cursor(raw=raw)
		try:
			cursor.execute(comm, args)
			self.l.debug(comm, args)
		except mysql.Error as err:
			if err.errno == mysql_errorcode.ER_DUP_ENTRY:  # Duplicate entry
				raise err
			self.l.error("Error running statement: {}".format(err))
		return cursor

	def run_named(self, comm, args, raw=False):
		cursor = None
		try:
			cursor = self.connection.cursor(raw=raw)
		except mysql.errors.OperationalError:
			self.l.warning('Reconnecting')
			self.connection.reconnect()
			cursor = self.connection.cursor(raw=raw)
		try:
			cursor.execute(comm, args)
			self.l.debug(comm, args)
		except mysql.Error as err:
			if err.errno == mysql_errorcode.ER_DUP_ENTRY:  # Duplicate entry
				raise err
			self.l.error("Error running statement: {}".format(err))
		return cursor

	def close(self):
		self.l.info('Connection closing down')
		self.connection.commit()
		self.l.info('Commited changes')
		self.connection.close()
		self.l.info('Closed connection')

	# "Public" functions
	def addUser(self, name, password, perms, img=DEFAULT_IMAGE):
		try:
			self.run('INSERT INTO users(uuid, name, name_low, passwd, perms, img) values(UUID(), %s, %s, %s, %s, %s)',
					 name, name.lower(), crypto.encrypt(password), perms, img).close()
		except mysql.Error:
			self.l.error('Duplicate username "%s"', name)
			raise UserDuplicateError('Duplicate username "%s"' % name)

	def changePassword(self, uuid, new_password):
		try:
			self.run('UPDATE users SET passwd = %s WHERE uuid = %s',
					 crypto.encrypt(new_password), uuid).close()
		except mysql.Error:
			self.l.error('Unexpected error setting the password')

	def deleteUsers(self):
		self.l.warning('DELETING USERS')

		self.run('DELETE FROM votes').close()
		self.run('DELETE FROM comments').close()
		self.run('DELETE FROM posts').close()
		self.run('DELETE FROM sessions').close()
		self.run('DELETE FROM users').close()

	def deleteUser(self, uuid):
		self.l.warning('DELETING USER %s', uuid)

		self.run('DELETE comments, posts FROM users LEFT JOIN posts on users.uuid = posts.author LEFT JOIN comments ON posts.uuid = comments.postid WHERE users.uuid = %s', uuid).close()
		self.run('DELETE users, comments FROM users LEFT JOIN comments on users.uuid = comments.userid WHERE users.uuid = %s', uuid).close()

	def checkPassword(self, username, password):
		cursor = self.run(
			'SELECT passwd FROM users WHERE name_low = %s', username.lower(), raw=True)
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			return crypto.validate(password, res[0][0])
		else:
			self.l.error('User %s is not present' % username)
			raise UserNotFoundError('User %s is not present' % username)

	def getUserUUID(self, username):
		cursor = self.run(
			'SELECT uuid FROM users WHERE name_low = %s', username.lower())
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			return res[0][0]
		else:
			self.l.error('User %s is not present' % username)
			raise UserNotFoundError('User %s is not present' % username)

	def getUserFromUUID(self, uuid):
		cursor = self.run('SELECT name FROM users WHERE uuid = %s', uuid)
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			return res[0]
		else:
			self.l.error('User %s is not present' % uuid)
			raise UserNotFoundError('User %s is not present' % uuid)

	def getUserPerms(self, uuid):
		cursor = self.run('SELECT perms FROM users WHERE uuid = %s', uuid)
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			return res[0][0]
		else:
			self.l.error('User %s is not present' % uuid)
			raise UserNotFoundError('User %s is not present' % uuid)

	def getUserImage(self, uuid):
		cursor = self.run(
			'SELECT img FROM users WHERE uuid = %s', uuid, raw=True)
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			return res[0][0]
		else:
			self.l.error('User %s is not present' % uuid)
			raise UserNotFoundError('User %s is not present' % uuid)

	def setUserImage(self, uuid, b64image):
		self.run('UPDATE users SET img = %s WHERE uuid = %s',
				 base64.b64decode(b64image), uuid).close()

	def createPost(self, title, authorid, content):
		self.run('INSERT INTO posts(uuid, title, author, content, timestamp) values(UUID(), %s, %s, %s, NOW())',
				 title, authorid, content).close()

	def getPosts(self):
		cursor = self.run(
			'SELECT posts.uuid, posts.title, users.name AS author, posts.timestamp FROM posts INNER JOIN(users) ON posts.author = users.uuid ORDER BY posts.timestamp DESC')
		posts = []
		for (uuid, title, author, timestamp) in cursor:
			post = {'uuid': uuid, 'title': title,
					'author': author, 'date': timestamp}
			posts.append(post)
		cursor.close()

		return posts

	def getPostsCount(self):
		cursor = self.run('SELECT COUNT(*) FROM posts')
		return cursor.fetchone()[0]

	def getPostsPaged(self, page):

		cursor = self.run('SELECT posts.uuid, posts.title, users.name AS author, posts.timestamp FROM posts INNER JOIN(users) ON posts.author = users.uuid ORDER BY posts.timestamp DESC LIMIT %s, %s',
						  POSTS_PER_PAGE * page, POSTS_PER_PAGE)
		posts = []
		for (uuid, title, author, timestamp) in cursor:
			post = {'uuid': uuid, 'title': title,
					'author': author, 'date': timestamp}
			posts.append(post)
		cursor.close()

		return posts

	def getPagesCount(self):
		return ceil(float(self.getPostsCount()) / float(POSTS_PER_PAGE))

	def searchPostsPaged(self, search, page):
		cursor = self.run_named("""
SELECT
	uuid,
	title,
	author,
	timestamp
FROM
	(
	SELECT
		(MATCH(title) AGAINST(`search`)) * 2 + (MATCH(content) AGAINST(`search`)) * 1 +
		(CASE
			WHEN 1 / CAST((NOW() - timestamp)* 0.0001 AS FLOAT) < 5 THEN 1 / CAST((NOW() - timestamp)* 0.0001 AS FLOAT)
			ELSE 5
		END) * 0.0001 AS relevance,
		uuid,
		author,
		title,
		timestamp
	FROM
		(
		SELECT
			%(search)s as `search`,
			posts.uuid as uuid,
			posts.title as title,
			users.name AS author,
			posts.timestamp as timestamp,
			posts.content as content
		FROM
			posts
		INNER JOIN(users) ON
			posts.author = users.uuid
		) as inner_matches
	) AS matches
WHERE
	relevance > 0.0005
ORDER BY
	relevance DESC LIMIT %(page)s, %(posts_per_page)s
""", {"search": search, "page": page * POSTS_PER_PAGE, "posts_per_page": POSTS_PER_PAGE})
		posts = []
		for (uuid, title, author, timestamp) in cursor:
			post = {'uuid': uuid, 'title': title,
					'author': author, 'date': timestamp}
			posts.append(post)
		cursor.close()

		return posts

	def getSearchPostsCount(self, search):
		cursor = self.run("""
SELECT
	count(*)
FROM
	(
	SELECT
		(MATCH(title) AGAINST(`search`)) * 2 + (MATCH(content) AGAINST(`search`)) * 1 +
		(CASE
			WHEN 1 / CAST((NOW() - timestamp)* 0.0001 AS FLOAT) < 5 THEN 1 / CAST((NOW() - timestamp)* 0.0001 AS FLOAT)
			ELSE 5
		END) * 0.0001 AS relevance,
		uuid,
		author,
		title,
		timestamp
	FROM
		(
		SELECT
			%s as `search`,
			posts.uuid as uuid,
			posts.title as title,
			users.name AS author,
			posts.timestamp as timestamp,
			posts.content as content
		FROM
			posts
		INNER JOIN(users) ON
			posts.author = users.uuid
		) as inner_matches
	) AS matches
WHERE
	relevance > 0.0005
ORDER BY
	relevance DESC
""", search)
		return cursor.fetchone()[0]
	
	def getSearchPagesCount(self, search):
		return ceil(float(self.getSearchPostsCount(search)) / float(POSTS_PER_PAGE))

	def getPost(self, uuid):
		cursor = self.run(
			'SELECT posts.title, users.name AS author, posts.timestamp, posts.content FROM posts INNER JOIN(users) ON posts.author = users.uuid WHERE posts.uuid = %s', uuid)
		res = cursor.fetchall()
		cursor.close()
		if len(res) == 1:
			post = res[0]
			return {'title': post[0], 'author': post[1], 'date': utils.formatPostDate(post[2]), 'content': post[3]}
		else:
			self.l.error('Post %s is non existant' % uuid)
			raise PostNotFoundError('Post %s is non existant' % uuid)

	def postComment(self, post_uuid, user_uuid, content, replyTo=None):
		self.run('INSERT INTO comments(uuid, userid, postid, content, timestamp, repliesto) values(UUID(), %s, %s, %s, NOW(), %s)',
				 user_uuid, post_uuid, content, replyTo).close()

	def getComments(self, post_uuid, user_uuid=None):
		cursor = self.run('SELECT comments.uuid, users.name, comments.userid, comments.content, comments.timestamp FROM comments INNER JOIN(users) ON comments.userid = users.uuid WHERE comments.postid = %s AND comments.repliesto IS NULL ORDER BY comments.timestamp ASC', post_uuid)
		comments = []
		for (uuid, username, useruuid, content, timestamp) in cursor.fetchall():
			comment = {'uuid': uuid, 'username': username, 'useruuid': useruuid, 'content': content, 'timestamp': utils.formatCommentDate(
				timestamp), 'replies': self.getReplies(uuid, user_uuid), 'points': self.getPoints(uuid)}
			if user_uuid:
				comment['vote'] = self.getVote(user_uuid, uuid)
			comments.append(comment)
		cursor.close()

		return comments

	def getReplies(self, comment_uuid, user_uuid=None):
		cursor = self.run('SELECT comments.uuid, users.name, comments.userid, comments.content, comments.timestamp FROM comments INNER JOIN(users) ON comments.userid = users.uuid WHERE comments.repliesto = %s ORDER BY comments.timestamp ASC', comment_uuid)
		comments = []
		for (uuid, username, useruuid, content, timestamp) in cursor.fetchall():
			comment = {'uuid': uuid, 'username': username, 'useruuid': useruuid, 'content': content, 'timestamp': utils.formatCommentDate(
				timestamp), 'replies': self.getReplies(uuid, user_uuid), 'points': self.getPoints(uuid)}
			if user_uuid:
				comment['vote'] = self.getVote(user_uuid, uuid)
			comments.append(comment)
		cursor.close()

		return comments

	def getVote(self, user_uuid, comment_uuid):
		cursor = self.run(
			'SELECT vote FROM votes WHERE useruuid = %s AND commentuuid = %s', user_uuid, comment_uuid)
		rows = cursor.fetchall()
		cursor.close()
		if len(rows) > 0:
			return rows[0][0]

	def vote(self, user_uuid, comment_uuid, vote):
		try:
			self.run('INSERT INTO votes(useruuid, commentuuid, vote) VALUES(%s, %s, %s)',
					 user_uuid, comment_uuid, vote).close()
		except mysql.Error:
			self.l.error('DUPLICATE VOTE, UPDATING INSTEAD')
			self.run('UPDATE votes SET vote = %s WHERE useruuid = %s AND commentuuid = %s',
					 vote, user_uuid, comment_uuid)

	def getPoints(self, comment):
		cursor = self.run(
			'SELECT vote, COUNT(*) FROM votes WHERE commentuuid = %s GROUP BY vote', comment)
		res = 0
		for (vote, num) in cursor.fetchall():
			if vote == 'UPVOTE':
				res += num
			elif vote == 'DOWNVOTE':
				res -= num
		cursor.close()
		return res

	def updateSessions(self):
		self.run('DELETE FROM sessions WHERE sessions.expiry < NOW()').close()

	def addSession(self, uuid):
		session_uuid = str(libUUID.uuid4())
		self.updateSessions()
		self.run('INSERT INTO sessions(uuid, userid, expiry) VALUES(%s, %s, NOW() + INTERVAL 1 DAY)',
				 session_uuid, uuid).close()
		return session_uuid

	def deleteSession(self, uuid):
		self.updateSessions()
		self.run('DELETE FROM sessions WHERE uuid = %s', uuid).close()

	def checkSession(self, session):
		self.updateSessions()
		cursor = self.run(
			'SELECT COUNT(uuid) FROM sessions WHERE uuid = %s', session)
		count = cursor.fetchall()[0][0]
		cursor.close()
		return count > 0

	def getUserUUIDFromSession(self, session):
		cursor = self.run(
			'SELECT userid FROM sessions WHERE uuid = %s', session)
		res = cursor.fetchall()
		cursor.close()
		if len(res) > 0:
			return res[0][0]
		else:
			raise UserNotFoundError()

# DB errors


class UserDuplicateError(Exception):
	pass


class UserNotFoundError(Exception):
	pass


class PostNotFoundError(Exception):
	pass
