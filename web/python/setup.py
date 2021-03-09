import json, os, time
from python import logger, db
from base64 import b64encode, b64decode
import rsa, os
from pathlib import Path

config = { # Default config
	'version': 2,
	'salt': os.urandom(40),
	'key': b64encode(os.urandom(40)).decode(),
	'db': {
		'version': 3,
		'user': 'coderbrothers',
		'password': 'coderbrothers' # Change this
	}
}

rsa_pub = None
rsa_priv = None

hasSetUp = False
settingUp = False

def newConfig(f, log):
	log.info('Creating config')
	fixed_json = dict(config)
	fixed_json['salt'] = b64encode(fixed_json['salt']).decode() # Encode bytes object
	json.dump(fixed_json, f, indent=4)

def setup():
	global config
	global settingUp
	global hasSetUp
	global rsa_pub
	global rsa_priv
	if not settingUp:
		start_time = time.time()
		settingUp = True
		delete_users = False
		logger.setup()
		log = logger.get('Setup')
		log.info('setup called')
		if not os.path.lexists('web/post'):
			os.mkdir('web/post')
		# Config loading / writing
		exiting = False
		try:
			with open('config.json') as f:
				log.info('Loading config')
				try:
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

					# print('version' in fixed_json['version'])
					
					if 'db' not in fixed_json:
						log.critical('Wrong config')
						exiting = True
					elif 'version' not in fixed_json['db']:
						log.critical('No DB version')
						exiting = True
					elif fixed_json['db']['version'] != config['db']['version']:
						log.critical('Wrong DB version')
						exiting = True
					if not exiting:
						config = fixed_json
				except json.decoder.JSONDecodeError:
					raise OldConfigError()
		except FileNotFoundError:
			with open('config.json', 'x') as f:
				newConfig(f, log)
		except OldConfigError:
			with open('config.json', 'w') as f:
				newConfig(f, log)
		
		if exiting:
			with open('config.json', 'w') as f:
				newConfig(f, log)
			log.critical('Please re-setup the DB (cat setup.sql | mysql -uroot -p)')
			log.critical('Now end this process with ctrl-c')
			time.sleep(1000000)
		hasSetUp = True
		if delete_users:
			db.getDB().deleteUsers()

		log.info("Checking for RSA keys")
		Path("certificates").mkdir(exist_ok=True)
		try:
			with open('certificates/private.pem', 'rb') as f:
				log.info('Loading private key')
				b = f.read()
				rsa_priv = rsa.PrivateKey.load_pkcs1(b)
				# load certs
			with open('certificates/public.pem', 'rb') as f:
				log.info('Loading public key')
				b = f.read()
				rsa_pub = rsa.PublicKey.load_pkcs1(b)
				# load certs
		except FileNotFoundError: # both certs have to be generated at the same time
			log.info("RSA keys not found. Generating new ones")
			(pub_pem, priv_pem) = gen_keys() # gen keys automatically saves them to the global vars
			with open('certificates/private.pem', 'wb') as f:
				f.write(priv_pem)
			with open('certificates/public.pem', 'wb') as f:
				f.write(pub_pem)
		elapsed = round(time.time()-start_time,2)
		log.info(f'Setup done in {elapsed}s')
		logger.remove(log)
	else:
		while not hasSetUp:
			time.sleep(1)
		return config

class OldConfigError(Exception):
	pass
	

def get_config(): # Only load config when needed
	global hasSetUp
	global config
	if not hasSetUp:
		setup()
	return config

def gen_keys():
	global rsa_pub
	global rsa_priv
	(pubkey, privkey) = rsa.newkeys(2048)
	rsa_pub = pubkey
	rsa_priv = privkey
	return (pubkey.save_pkcs1(), privkey.save_pkcs1())

def get_pub_key():
	global rsa_pub
	return rsa_pub

def get_priv_key():
	global rsa_priv
	return rsa_priv