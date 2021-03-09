from os import path, mkdir
from scss.compiler import compile_file
import scss
from python import logger
from python import rcssmin


def compile(file):
	log = logger.get('SCSS')
	p = path.splitext(file)[0]
	if not path.exists('web/css'):
		mkdir('web/css')
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
		s = None
		try:
			s = compile_file(scss_file)
		except scss.errors.SassError as e:
			log.error(f'SCSS error on file {scss_file}:')
			log.error(e)
			s = e.to_css() + 'body > * {visibility: hidden}'
		if s:
			s = rcssmin.cssmin(s)
			with open(css_file, 'w') as css:
				# log.info(s)
				css.write(s)

	else:
		log.info(f'{css_file} already compiled')
