import json, os
from base64 import b64encode, b64decode

config = { # Default config
	'salt': os.urandom(20),
	'db': {
		'user': 'coderbrothers',
		'password': 'coderbrothers' # Change this
	}
}

def setup():
	global config
	print('Setting up')
	try:
		with open('config.json') as f:
			print('Loading config')
			fixed_json = json.load(f)
			fixed_json['salt'] = b64decode(fixed_json['salt'].encode()) # Decode bytes object
			config = fixed_json
	except FileNotFoundError:
		with open('config.json', 'x') as f:
			print('Creating config')
			fixed_json = config
			fixed_json['salt'] = b64encode(fixed_json['salt']).decode() # Encode bytes object
			json.dump(fixed_json, f)
	

def get_config():
	return config