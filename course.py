#!/usr/bin/python3
import re
import html
import subprocess
import sys

# OPTIONS #
filename = 'test' # text file to process (in src/ directory)
tplname  = 'default' # template file (in tpl/ directory)

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

with open('src/' + filename, 'r') as src_in:
	src = src_in.read()

print('Parsing input file...')

r = '\n(%s)\\s*:\\s*(?i)' % ('|'.join(keywords),)
s = re.split(r, src)
data = {k.lower(): v for k, v in zip(s[1::2], s[2::2])}

header = s[0]
header_data = re.match('^\\s*(?P<titre>.*?)\\s*(?:\\((?P<voie>.*)\\))?\\s*$(?s)', header).groupdict()
data.update(header_data)


print('Loading template %s...' % (tplname,))

with open('tpl/%s.svg' % (tplname,), 'r') as tpl_in:
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

with open('output/%s.svg' % (filename,), 'w') as tpl_out:
	tpl_out.write(tpl)


print('Output final image in output/%s.png...' % (filename,))

subprocess.call(['inkscape', 'output/%s.svg'% (filename,), '-e', 'output/%s.png' % (filename,), '-d', '300'])

print('Done.')
