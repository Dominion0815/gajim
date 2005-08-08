##	gtkgui_helpers.py
##
## Gajim Team:
##	- Yann Le Boulanger <asterix@lagaule.org>
##	- Vincent Hanquez <tab@snarc.org>
##	- Nikos Kouremenos <kourem@gmail.com>
##	- Dimitur Kirov <dkirov@gmail.com>
##
## This file was initially written by Dimitur Kirov
##
##	Copyright (C) 2003-2005 Gajim Team
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##

import xml.sax.saxutils
import gtk
import os
from common import i18n
i18n.init()
_ = i18n._
from common import gajim

def reduce_chars_newlines(text, max_chars = 0, max_lines = 0, 
	widget = None):
	''' Cut the chars after 'max_chars' on each line
	and show only the first 'max_lines'. If there is more text
	to be shown, display the whole text in tooltip on 'widget'
	If any of the params is not present(None or 0) the action
	on it is not performed
	'''
	def _cut_if_long(str):
		if len(str) > max_chars:
			str = str[:max_chars - 3] + '...'
		return str
	
	if max_lines == 0:
		lines = text.split('\n')
	else:
		lines = text.split('\n', max_lines)[:max_lines]
	if max_chars > 0:
		if lines:
			lines = map(lambda e: _cut_if_long(e), lines)
	if lines:
		reduced_text = reduce(lambda e, e1: e + '\n' + e1, lines)
	else:
		reduced_text = ''
	if reduced_text != text and widget is not None:
		pass # FIXME show tooltip
	return reduced_text
	
def convert_bytes(string):
	suffix = ''
	# IEC standard says KiB = 1024 bytes KB = 1000 bytes
	use_kib_mib = gajim.config.get('use_kib_mib')
	align = 1024.
	bytes = float(string)
	if bytes >= align:
		bytes = round(bytes/align, 1)
		if bytes >= align:
			bytes = round(bytes/align, 1)
			if bytes >= align:
				bytes = round(bytes/align, 1)
				if use_kib_mib:
					#GiB means gibibyte
					suffix = _('%s GiB') 
				else:
					#GB means gigabyte
					suffix = _('%s GB')
			else:
				if use_kib_mib:
					#MiB means mibibyte
					suffix = _('%s MiB')
				else:
					#MB means megabyte
					suffix = _('%s MB')
		else:
			if use_kib_mib:
					#KiB means kibibyte
					suffix = _('%s KiB')
			else:
				#KB means kilo bytes
				suffix = _('%s KB')
	else:
		#B means bytes 
		suffix = _('%s B')
	return suffix % str(bytes)
	
def escape_for_pango_markup(string):
	# escapes < > & \ "
	# for pango markup not to break
	if string is None:
		return
	if gtk.pygtk_version >= (2, 8, 0) and gtk.gtk_version >= (2, 8, 0):
		escaped_str = gobject.markup_escape_text(string)
	else:
		escaped_str =xml.sax.saxutils.escape(string, {'\\': '&apos;',
			'"': '&quot;'})
	
	return escaped_str

def autodetect_browser_mailer():
	#recognize the environment for appropriate browser/mailer
	if os.path.isdir('/proc'):
		# under Linux: checking if 'gnome-session' or
		# 'startkde' programs were run before gajim, by
		# checking /proc (if it exists)
		#
		# if something is unclear, read `man proc`;
		# if /proc exists, directories that have only numbers
		# in their names contain data about processes.
		# /proc/[xxx]/exe is a symlink to executable started
		# as process number [xxx].
		# filter out everything that we are not interested in:
		files = os.listdir('/proc')

		# files that doesn't have only digits in names...
		files = filter(str.isdigit, files)

		# files that aren't directories...
		files = filter(lambda f:os.path.isdir('/proc/' + f), files)

		# processes owned by somebody not running gajim...
		# (we check if we have access to that file)
		files = filter(lambda f:os.access('/proc/' + f +'/exe', os.F_OK), files)

		# be sure that /proc/[number]/exe is really a symlink
		# to avoid TBs in incorrectly configured systems
		files = filter(lambda f:os.path.islink('/proc/' + f + '/exe'), files)

		# list of processes
		processes = [os.path.basename(os.readlink('/proc/' + f +'/exe')) for f in files]
		if 'gnome-session' in processes:
			gajim.config.set('openwith', 'gnome-open')
		elif 'startkde' in processes:
			gajim.config.set('openwith', 'kfmclient exec')
		else:
			gajim.config.set('openwith', 'custom')
