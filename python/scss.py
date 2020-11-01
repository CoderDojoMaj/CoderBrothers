from os import path
from scss.compiler import compile_file
from python import logger

def compile(file):
	log = logger.get('SCSS')
	p = path.splitext(file)[0]
	css_file = path.join('web/css', p + '.css')
	scss_file = path.join('web/scss', p + '.scss')
	c = False
	if path.exists(css_file):
		if path.getmtime(css_file) < path.getmtime(scss_file):
			c = True
	else:
		c = True
	
	if c:
		log.info(f'Recompiling {css_file}')
		with open(css_file, 'w') as css:
			s = compile_file(scss_file)
			# log.info(s)
			css.write(s)
	else:
		log.info(f'{css_file} already compiled')
	

