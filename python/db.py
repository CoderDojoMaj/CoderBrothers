from mysql import connector as mysql
from mysql.connector import errorcode as mysql_errorcode
from python import setup, logger, crypto
import atexit

db = None

def getDB(): # Only get a single DB object (singleton)
    global db
    if db is None:
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
    
    def addUser(self, name, password, perms, img=None):
        try:
            self.run('INSERT INTO users(uuid, name, name_low, passwd, perms, img) values(UUID(), %s, %s, %s, %s, %s)', name, name.lower(), crypto.encrypt(password), perms, img).close()
        except mysql.Error:
            self.l.error('Duplicate username "%s"', name)
            raise UserDuplicateError('Duplicate username "%s"' % name)
    
    def getUsers(self): # Testing function
        for (uuid, name, perms, passwd, img) in self.run('SELECT uuid, name, perms, hex(passwd), hex(img) FROM users'):
            print(uuid, name, perms, passwd, img)
    
    def checkPassword(self, username, password):
        cursor = self.run('SELECT hex(passwd) FROM users WHERE name_low = %s', username.lower())
        res = cursor.fetchall()
        cursor.close()
        if len(res) == 1:
            return crypto.validate(password, bytes.fromhex(res[0][0]))
        else:
            self.l.error('User %s is not present' % username)
            raise UserNotFoundError('User %s is not present' % username)

class UserDuplicateError(Exception):
    pass

class UserNotFoundError(Exception):
    pass