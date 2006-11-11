# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005 Vasco Nunes
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

import smtplib
import gutils
from gettext import gettext as _

def mailto(self, server, auth, user, password, sender, to, subject, msg):
	"""
	sends an email
	"""
	session = smtplib.SMTP(server)
	session.set_debuglevel(1)
	if auth:
		try:
			session.login(user, password)
		except:
			gutils.info(self, _("Error sending e-mail: %s")%"login failure", \
				self.widgets['window'])
			return
	headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" \
		% (sender, to, subject)
	try:
		smtpresult = session.sendmail(sender, to, headers+msg)
		gutils.info(self, _("E-mail sent sucessuly"), self.widgets['window'])
		return
	except:
		gutils.info(self, _("Error sending e-mail: %s")%"", self.widgets['window'])

def send_email(self):
	if len(self.person_email):
		if self.config.get('mail_use_auth', "False") == "True":
			use_auth = 1
		else:
			use_auth = 0
		mailto(self, self.config.get('mail_smtp_server', "localhost"), \
			use_auth, self.config.get('mail_username', ""), \
			self.config.get('mail_password', ""), \
			self.config.get('mail_email', "griffith"), self.person_email, \
			_("Movie loan reminder"), _("Hi, %s!\n\nJust to reminder you " + \
			"that I'm really needing the following movie I have loaned you " + \
			"recently:\n\n%s (%s)\n\nLoaned on %s") \
			%(self.person_name, self.widgets['movie']['o_title'].get_text(), \
			self.widgets['movie']['title'].get_text(), self.loan_date[:10]))
	else:
		gutils.info(self, _("This person has no e-mail address defined."), \
			self.widgets['window'])
