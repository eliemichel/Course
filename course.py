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
filename = 'test'    # Default text file to process (in src_dir directory)
tplname  = 'default' # Default template file (in tpl_dir directory)

# List of keywords. Must be in lower case.
keywords = [
	'altitude',
	'année',
	'vallée',
	'difficulté',
	'départ',
	'refuge',
	'temps',
	'dénivelée',
	'temps',
	'groupe',
	'souvenirs',
]
###########

print('Reading command line arguments...')

cur = ''
for arg in sys.argv[1:]:
	if cur != '':
		#opt[cur] = arg
		if cur == 'tplname':
			tplname = arg
	else:
		if arg == '-t' or arg == '--template':
			cur = 'tplname'
		else:
			filename = arg


print('Loading file %s...' % (filename,))

with open(join(src_dir, filename), 'r') as src_in:
	src = src_in.read()

print('Parsing input file...')

r = '\n(%s)\\s*:\\s*(?i)' % ('|'.join(keywords),)
s = re.split(r, src)
data = {k.lower(): v for k, v in zip(s[1::2], s[2::2])}

header = s[0]
header_data = re.match('^\\s*(?P<titre>.*?)\\s*(?:\\((?P<voie>.*)\\))?\\s*$(?s)', header).groupdict()
data.update(header_data)


print('Loading template %s...' % (tplname,))

with open(join(tpl_dir, tplname + '.svg'), 'r') as tpl_in:
	tpl = tpl_in.read()


print('Building vectorial image...')

def replace(v):
	v = html.escape(v).strip('\n')
	def _(match):
		d = match.groupdict()
		open_tag = '<flowPara%s>' % (d['options'],)
		return open_tag + d['prefix'] + v.replace('\n', '</flowPara>' + open_tag)
	return _

for k, v in data.items():
	tpl = re.sub('<flowPara(?P<options>.*?)>(?P<prefix>.*?)%%%s%%' % (k,), replace(v), tpl)

with open(join(out_dir, filename + '.svg'), 'w') as tpl_out:
	tpl_out.write(tpl)


print('Output final image in %s...' % (join(out_dir, filename + '.png'),))

subprocess.call(['inkscape', join(out_dir, filename + '.svg'), '-e', join(out_dir, filename + '.png'), '-d', '300'])

print('Done.')
