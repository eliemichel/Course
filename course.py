#!/usr/bin/python3
import re
import html
import subprocess
import sys
from os.path import join

# OPTIONS #
src_dir  = 'src'     # Directory that contains "Course" files
tpl_dir  = 'tpl'     # Directory that contains templates
out_dir  = 'output'  # Directory where created files are stored
default_tplname = 'default.svg' # Default template file (in tpl_dir directory)
loglevel = 3         # Log level (amount of information displayed). -1: mute (not implemented), 0: Error only, 1: Warnings, 2: Info, 3: Verbose

# List of keywords. Must be in lower case.
keywords = [
	'altitude',
	'année',
	'vallée',
	'difficulté',
	'départ',
	'refuge',
	'temps',
	'dénivelé',
	'temps',
	'groupe',
	'souvenirs',
]
###########


def log(msg, level=2):
	"""Print log messages whom level is bellow loglevel
	level: -1: mute (not implemented), 0: Error only, 1: Warnings, 2: Info, 3: Verbose"""
	if level <= loglevel:
		print(msg)


class Course():
	"""Parse and export Course files."""
	def __init__(self, filename, tplname=None):
		self.filename = filename
		self.tplname  = tplname or default_tplname

	def load(self, filename=None):
		self.filename = filename or self.filename
		f = join(src_dir, self.filename)
		log('Loading file %s...' % (f,))
		with open(f, 'r') as src:
			self.src = src.read()

	def load_template(self, tplname=None):
		self.tplname = tplname or self.tplname
		f = join(tpl_dir, self.tplname)
		log('Loading template %s...' % (f,))
		with open(f, 'r') as tpl:
			self.tpl = tpl.read()

	def parse(self):
		log('Parsing input file...')
		r = '(%s)\\s*:\\s*(?i)' % ('|'.join(keywords),)
		s = re.split(r, self.src)
		self.data = {k.lower(): v for k, v in zip(s[1::2], s[2::2])}

		header = s[0]
		header_data = re.match('^\\s*(?P<titre>.*?)\\s*(?:\\((?P<voie>.*)\\))?\\s*$(?s)', header).groupdict()
		self.data.update(header_data)

	def make_svg(self):
		log('Building vectorial image...')

		def replace(v):
			v = html.escape(v).replace('\r\n', '\n').strip('\n')
			def _(match):
				d = match.groupdict()
				open_tag = '<flowPara%s>' % (d['options'],)
				return open_tag + d['prefix'] + v.replace('\n', '</flowPara>' + open_tag)
			return _

		self.svg_file = self.tpl
		for k, v in self.data.items():
			self.svg_file = re.sub('<flowPara(?P<options>.*?)>(?P<prefix>.*?)%%%s%%' % (k,), replace(v), self.svg_file)

	def save_svg(self, f=None):
		f = f or join(out_dir, self.filename + '.svg')
		log('Save SVG image to %s...' % (f,))
		with open(f, 'wb') as out:
			out.write(self.svg_file.encode('utf-8'))

	def save_png(self, f=None, save_svg=True):
		f_png = f or join(out_dir, self.filename + '.png')
		f_svg = join(out_dir, self.filename + '.svg')
		if save_svg: self.save_svg(f_svg)
		log('Save PNG image to %s...' % (f_png,))
		log('== Inkscape output ==')
		subprocess.call(['inkscape', f_svg, '-e', f_png, '-d', '300'])
		log('== End of Inkscape output ==')
	
	def save_jpg(self, f=None, save_png=True):
		f_jpg = f or join(out_dir, self.filename + '.jpg')
		f_png = join(out_dir, self.filename + '.png')
		if save_png: self.save_png(f_png)
		log('Save JPG image to %s...' % (f_jpg,))
		log('== ImageMagick output ==')
		subprocess.call(['magick', 'convert', f_png, f_jpg])
		log('== End of ImageMagick output ==')

	def export_svg(self):
		self.load()
		self.load_template()
		self.parse()
		self.make_svg()
		self.save_svg()

	def export_png(self):
		self.export_svg()
		self.save_png(save_svg=False)
		
	def export_jpg(self):
		self.export_png()
		self.save_jpg(save_png=False)


def parse_args(options, argv=None):
	"""Parse args from [argv] (default to sys.argv) and return a dict associating values to option names. Remaining args are listed in Ellipsis entry of the returned dict."""
	argv = argv or sys.argv[1:]
	args = {o: None for o in options.values()}
	args[...] = [] # Remaining arguments
	cur = None
	for arg in argv:
		if cur != None:
			args[cur] = arg
			cur = None
		else:
			if arg in options:
				cur = options[arg]
			else:
				args[...].append(arg)

	return args



if __name__ == '__main__':

	args = parse_args({
		'-t': 'tplname',
		'--template': 'tplname',
	})

	if len(args[...]) < 1:
		print('Entrez le nom de la course : ', end='')
		course = input()
		args[...] = [course]

	name = args[...][0]

	c = Course(name, args['tplname'])
	c.export_jpg()

	log('Done.')
