#!/usr/bin/python3
import re
import html
import subprocess

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

for k, v in data.items():
	tpl = tpl.replace('&lt;%s&gt;' % (k,), html.escape(v).replace('\n', '</flowPara><flowPara>'))

with open('output/%s.svg' % (tplname,), 'w') as tpl_out:
	tpl_out.write(tpl)


print('Output final image in output/%s.png...' % (tplname,))

subprocess.call(['inkscape', 'output/%s.svg'% (tplname,), '-e', 'output/%s.png' % (tplname,)])

print('Done.')
