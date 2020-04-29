import json, os, time
from python import logger, db
from base64 import b64encode, b64decode

config = { # Default config
	'version': 2,
	'salt': os.urandom(40),
	'key': b64encode(os.urandom(40)).decode(),
	'db': {
		'user': 'coderbrothers',
		'password': 'coderbrothers' # Change this
	}
}

hasSetUp = False
settingUp = False

def newConfig(f, log):
	log.info('Creating config')
	fixed_json = dict(config)
	fixed_json['salt'] = b64encode(fixed_json['salt']).decode() # Encode bytes object
	json.dump(fixed_json, f)

def setup():
	global config
	global settingUp
	global hasSetUp
	if not settingUp:
		settingUp = True
		delete_users = False
		logger.setup()
		log = logger.get('Setup')
		log.info('setup called')
		# Config loading / writing
		try:
			with open('config.json') as f:
				log.info('Loading config')
				fixed_json = json.load(f)
				if 'salt' in fixed_json:
					fixed_json['salt'] = b64decode(fixed_json['salt'].encode()) # Decode bytes object
					if len(fixed_json['salt']) == len(config['salt']):
						log.info('Saving salt')
						config['salt'] = fixed_json['salt']
					else:
						log.warning('Changing salt, old passwords WON\'T WORK')
						delete_users = True
				
				if 'version' not in fixed_json:
					log.warning('No config version')
					raise OldConfigError()
				elif fixed_json['version'] != config['version']:
					log.warning('Old config')
					raise OldConfigError()
				
				config = fixed_json
		except FileNotFoundError:
			with open('config.json', 'x') as f:
				newConfig(f, log)
		except OldConfigError:
			with open('config.json', 'w') as f:
				newConfig(f, log)
		hasSetUp = True
		if delete_users:
			db.getDB().deleteUsers()
		log.info('Setup done')
		logger.remove(log)
	else:
		time.sleep(3)
		return config

class OldConfigError(Exception):
	pass
	

def get_config(): # Only load config when needed
	global hasSetUp
	global config
	if not hasSetUp:
		setup()
	return config