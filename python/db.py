from mysql import connector as mysql
from mysql.connector import errorcode as mysql_errorcode
from python import setup, logger, crypto, utils
import atexit

db = None
db_started = False

def getDB(): # Only get a single DB object (singleton)
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
            self.connection = mysql.connect(user=config['user'], password=config['password'], database='coderbrothers')
            self.l.info('Connection started')
        except mysql.Error as err:
            if err.errno == mysql.errorcode.ER_ACCESS_DENIED_ERROR:
                self.l.critical("Something is wrong with your user name or password")
            elif err.errno == mysql.errorcode.ER_BAD_DB_ERROR:
                self.l.critical("Database does not exist")
            else:
                self.l.critical(err)
            exit(1)
        
        if self.connection is None:
                self.l.critical('Couldn\'t connect to the database')
                exit(1)
        
        atexit.register(self.close)
    

    def run(self, comm, *args):
        cursor = None
        try:
            cursor = self.connection.cursor()
        except mysql.errors.OperationalError:
            self.l.warning('Reconnecting')
            self.connection.reconnect()
            cursor = self.connection.cursor()
        try:
            cursor.execute(comm, args)
            self.l.debug(comm, args)
        except mysql.Error as err:
            if err.errno == mysql_errorcode.ER_DUP_ENTRY: # Duplicate entry
                raise err
            self.l.error("Error running statement: {}".format(err))
        return cursor
    
    def close(self):
        self.l.info('Connection closing down')
        self.connection.commit()
        self.connection.close()
    
    # "Public" functions
    def addUser(self, name, password, perms, img=None):
        try:
            self.run('INSERT INTO users(uuid, name, name_low, passwd, perms, img) values(UUID(), %s, %s, %s, %s, %s)', name, name.lower(), crypto.encrypt(password), perms, img).close()
        except mysql.Error:
            self.l.error('Duplicate username "%s"', name)
            raise UserDuplicateError('Duplicate username "%s"' % name)
    
    def deleteUsers(self):
        self.l.warning('DELETING USERS')
        
        self.run('DELETE comments, posts FROM users LEFT JOIN posts on users.uuid = posts.author LEFT JOIN comments on posts.uuid = comments.postid').close()
        self.run('DELETE users, comments FROM users LEFT JOIN comments on users.uuid = comments.userid').close()
    
    def checkPassword(self, username, password):
        cursor = self.run('SELECT hex(passwd) FROM users WHERE name_low = %s', username.lower())
        res = cursor.fetchall()
        cursor.close()
        if len(res) == 1:
            return crypto.validate(password, bytes.fromhex(res[0][0]))
        else:
            self.l.error('User %s is not present' % username)
            raise UserNotFoundError('User %s is not present' % username)
    
    def createPost(self, title, authorid, content):
        self.run('INSERT INTO posts(uuid, title, author, content, timestamp) values(UUID(), %s, %s, %s, NOW())', title, authorid, content).close()
    
    def getPosts(self):
        cursor = self.run('SELECT posts.uuid, posts.title, users.name AS author, posts.timestamp FROM posts INNER JOIN(users) ON posts.author = users.uuid ORDER BY posts.timestamp DESC')
        posts = []
        for (uuid, title, author, timestamp) in cursor:
            post = {'uuid': uuid, 'title': title, 'author': author, 'date': timestamp}
            posts.append(post)
        cursor.close()
        
        return posts
    
    def getPost(self, uuid):
        cursor = self.run('SELECT posts.title, users.name AS author, posts.timestamp, posts.content FROM posts INNER JOIN(users) ON posts.author = users.uuid WHERE posts.uuid = %s', uuid)
        res = cursor.fetchall()
        cursor.close()
        if len(res) == 1:
            post = res[0]
            return {'title': post[0], 'author': post[1], 'date': utils.formatPostDate(post[2]), 'content': post[3]}
        else:
            self.l.error('Post %s is non existant' % uuid)
            raise PostNotFoundError('Post %s is non existant' % uuid)

## DB errors
class UserDuplicateError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class PostNotFoundError(Exception):
    pass